import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)

from config import settings
from predictor import ProgressionService

from autosoc_api.db.models.prediction import Prediction
from autosoc_api.services.prediction_idempotency import prediction_input_fingerprint
from autosoc_api.services.worker_reliability import RedisRetryState
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
            return False

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
            return True

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
            return True

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
        model_name = "Markov Baseline"
        model_version = "1.0"
        attack_version = "v14.1"
        fingerprint = prediction_input_fingerprint(
            incident_id=incident_uuid,
            model_name=model_name,
            model_version=model_version,
            attack_version=attack_version,
            observed_techniques=observed,
        )
        prediction_values = dict(
            incident_id=incident_uuid,
            model_name=model_name,
            model_version=model_version,
            attack_version=attack_version,
            input_fingerprint=fingerprint,

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
        result = await session.execute(
            insert(Prediction)
            .values(**prediction_values)
            .on_conflict_do_nothing(constraint="uq_predictions_logical_input")
            .returning(Prediction.id)
        )
        await session.commit()
        if result.scalar_one_or_none() is None:
            logger.info("Prediction already persisted for incident %s; acknowledged retry", incident_id)
        else:
            logger.info("Prediction successfully saved for incident %s", incident_id)
        return True

    except Exception as e:

        logger.exception(
            f"Error processing message: {e}"
        )

        await session.rollback()
        return False


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
        enable_auto_commit=False,
    )
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda value: json.dumps(value, default=str).encode("utf-8"),
    )
    retry_state = RedisRetryState(
        settings.REDIS_URL,
        "prediction",
        max_attempts=settings.RETRY_MAX_ATTEMPTS,
        base_delay_seconds=settings.RETRY_BASE_DELAY_SECONDS,
        max_delay_seconds=settings.RETRY_MAX_DELAY_SECONDS,
    )

    await consumer.start()
    await producer.start()

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

            message_key = retry_state.message_key(msg.topic, msg.partition, msg.offset)
            while True:
                async with async_session() as session:
                    processed = await process_message(msg.value, session, service)
                if processed:
                    # Offset advances only after the insert/upsert transaction is durable.
                    await retry_state.acknowledge(message_key)
                    await consumer.commit()
                    break

                decision = await retry_state.record_failure(
                    message_key,
                    RuntimeError("prediction processing was not durable"),
                )
                if decision.exhausted:
                    try:
                        await producer.send_and_wait(
                            settings.FAILED_TOPIC,
                            {
                                "failure_id": str(uuid.uuid4()),
                                "received_at": datetime.now(timezone.utc).isoformat(),
                                "failure_stage": "prediction",
                                "failure_reason_code": "RETRY_EXHAUSTED",
                                "failure_description": "Prediction failed after bounded retries",
                                "retryable": False,
                                "retry_count": decision.attempt,
                                "safe_metadata": {
                                    "topic": msg.topic,
                                    "partition": msg.partition,
                                    "offset": msg.offset,
                                },
                            },
                        )
                    except Exception:
                        logger.exception("Prediction DLQ publish failed; retaining Kafka offset")
                        await asyncio.sleep(decision.delay_seconds)
                        continue
                    logger.error("Retry exhausted for prediction message %s", message_key)
                    await retry_state.acknowledge(message_key)
                    await consumer.commit()
                    break
                await asyncio.sleep(decision.delay_seconds)

    except asyncio.CancelledError:

        logger.info(
            "Prediction worker shutting down..."
        )

    finally:

        await consumer.stop()
        await producer.stop()
        await retry_state.close()
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(consume())
