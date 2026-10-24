import asyncio
import json
import logging

from aiokafka import AIOKafkaConsumer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)

from config import settings
from predictor import ProgressionService

from autosoc_api.db.models.prediction import Prediction
from autosoc_api.db.models.attack import (
    IncidentAttackMapping,
    AttackTechnique,
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def process_message(
    msg_value,
    session: AsyncSession,
    service: ProgressionService
):
    """
    Process an incident update and generate a prediction.

    Kafka message format:
        {"incident_id": "uuid"}
    """

    try:
        # ---------------------------------------------------------
        # 1. Decode Kafka message
        # ---------------------------------------------------------
        if isinstance(msg_value, bytes):
            msg_value = msg_value.decode("utf-8")

        data = json.loads(msg_value)

        incident_id = data.get("incident_id")

        if not incident_id:
            logger.warning("Kafka message missing incident_id")
            return

        logger.info(
            f"Processing incident: {incident_id}"
        )

        # ---------------------------------------------------------
        # 2. Fetch ATT&CK mappings
        #
        # IMPORTANT:
        # Do NOT access m.technique.external_id directly.
        # That causes the greenlet_spawn async SQLAlchemy error.
        # ---------------------------------------------------------
        stmt = (
            select(
                IncidentAttackMapping,
                AttackTechnique.external_id
            )
            .join(
                AttackTechnique,
                IncidentAttackMapping.technique_id
                == AttackTechnique.id
            )
            .where(
                IncidentAttackMapping.incident_id == incident_id
            )
            .order_by(
                IncidentAttackMapping.created_at.asc()
            )
        )

        result = await session.execute(stmt)

        rows = result.all()

        logger.info(
            f"Found {len(rows)} attack-technique mappings "
            f"for incident {incident_id}"
        )

        if not rows:
            logger.warning(
                f"No attack mappings found for incident {incident_id}"
            )
            return

        # ---------------------------------------------------------
        # 3. Convert database mappings into predictor input
        # ---------------------------------------------------------
        mapping_dicts = []

        for mapping, external_id in rows:

            mapping_dicts.append(
                {
                    "technique_id": external_id,
                    "status": mapping.status,
                    "mapped_at": (
                        mapping.mapped_at.isoformat()
                        if mapping.mapped_at
                        else None
                    ),
                    "created_at": (
                        mapping.created_at.isoformat()
                        if mapping.created_at
                        else None
                    ),
                }
            )

        logger.info(
            f"Observed techniques: "
            f"{[m['technique_id'] for m in mapping_dicts]}"
        )

        # ---------------------------------------------------------
        # 4. Run Markov prediction
        # ---------------------------------------------------------
        prediction_result = service.predict(mapping_dicts)

        predictions = prediction_result.get(
            "predictions",
            []
        )

        observed = prediction_result.get(
            "observed",
            []
        )

        logger.info(
            f"Observed sequence: {observed}"
        )

        logger.info(
            f"Predicted techniques: {predictions}"
        )

        # Nothing to predict
        if not predictions:
            logger.info(
                f"No predictions generated for incident "
                f"{incident_id}"
            )
            return

        # ---------------------------------------------------------
        # 5. Calculate escalation risk
        #
        # For now we use the highest prediction probability.
        # ---------------------------------------------------------
        escalation_risk_score = max(
            (
                float(p.get("probability", 0.0))
                for p in predictions
            ),
            default=0.0
        )

        # ---------------------------------------------------------
        # 6. Convert UUID/string safely
        # ---------------------------------------------------------
        from uuid import UUID

        incident_uuid = UUID(str(incident_id))

        # ---------------------------------------------------------
        # 7. Create prediction record
        # ---------------------------------------------------------
        pred_record = Prediction(
            incident_id=incident_uuid,
            model_name="Markov Baseline",
            model_version="1.0",
            attack_version="v14.1",

            # JSONB-safe values
            observed_techniques=[
                str(tech)
                for tech in observed
            ],

            predicted_next_techniques=[
                {
                    "technique_id": str(
                        p["technique_id"]
                    ),
                    "probability": float(
                        p["probability"]
                    ),
                    "score": float(
                        p["score"]
                    ),
                }
                for p in predictions
            ],

            escalation_risk_score=float(
                escalation_risk_score
            ),
        )

        # ---------------------------------------------------------
        # 8. Save prediction
        # ---------------------------------------------------------
        session.add(pred_record)

        await session.commit()

        logger.info(
            f"Prediction successfully saved for "
            f"incident {incident_id}"
        )

    except Exception as e:

        logger.exception(
            f"Error processing message: {e}"
        )

        await session.rollback()


async def consume():

    # -------------------------------------------------------------
    # Database
    # -------------------------------------------------------------
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
    )

    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # -------------------------------------------------------------
    # Markov prediction service
    # -------------------------------------------------------------
    service = ProgressionService(
        settings.MODEL_PATH,
        settings.VOCAB_PATH,
    )

    # -------------------------------------------------------------
    # Kafka consumer
    # -------------------------------------------------------------
    consumer = AIOKafkaConsumer(
        settings.INCIDENTS_TOPIC,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id="prediction-worker-group",
        auto_offset_reset="earliest",
        enable_auto_commit=True,
    )

    await consumer.start()

    try:

        logger.info(
            "Prediction worker started consuming..."
        )

        async for msg in consumer:

            logger.info(
                f"Received Kafka message: "
                f"partition={msg.partition}, "
                f"offset={msg.offset}"
            )

            async with async_session() as session:

                await process_message(
                    msg.value,
                    session,
                    service,
                )

    except asyncio.CancelledError:

        logger.info(
            "Prediction worker shutting down..."
        )

    finally:

        await consumer.stop()
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(consume())