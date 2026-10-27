from typing import List, Any
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from autosoc_api.db.session import get_db_session
from autosoc_api.auth.dependencies import require_permission
from autosoc_api.auth.permissions import Permissions
from autosoc_api.auth.models import Principal
from autosoc_api.db.models.prediction import Prediction
from autosoc_api.services.prediction_idempotency import prediction_input_fingerprint
from autosoc_api.db.models.incident import Incident
from autosoc_api.schemas.prediction import PredictionResult, TechniquePrediction, PredictionTarget

router = APIRouter()

from datetime import datetime, timedelta, timezone

async def compute_and_save_prediction(incident: Incident, db: AsyncSession) -> Prediction:
    """
    Computes an attack progression prediction using Markov chain sequence transition rules
    and persists it into the predictions PostgreSQL database.
    """
    # Invoke Markov Chain Sequence Transition Predictor
    from autosoc_api.services.markov_predictor import markov_predictor
    pred_data = markov_predictor.predict_attack_progression(incident.title or "Security Event")
    
    observed = pred_data["observed_techniques"]
    predicted_next = pred_data["predicted_next_techniques"]
    target = pred_data["predicted_target"]
    path_continuation = pred_data["path_continuation"]
    risk_score = pred_data["escalation_risk_score"]

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    model_name = "Markov-Chain-ATT&CK-Predictor"
    model_version = "v1.2.0"
    attack_version = "v14.1"
    fingerprint = prediction_input_fingerprint(
        incident_id=incident.id,
        model_name=model_name,
        model_version=model_version,
        attack_version=attack_version,
        observed_techniques=observed,
    )
    existing = await db.execute(
        select(Prediction).where(
            Prediction.incident_id == incident.id,
            Prediction.model_name == model_name,
            Prediction.model_version == model_version,
            Prediction.attack_version == attack_version,
            Prediction.input_fingerprint == fingerprint,
        )
    )
    existing_prediction = existing.scalars().first()
    if existing_prediction:
        return existing_prediction

    prediction = Prediction(
        id=uuid.uuid4(),
        incident_id=incident.id,
        generated_at=now,
        valid_until=now + timedelta(hours=24),
        is_stale=False,
        model_name=model_name,
        model_version=model_version,
        attack_version=attack_version,
        input_fingerprint=fingerprint,
        status="completed",
        observed_techniques=observed,
        predicted_next_techniques=predicted_next,
        predicted_target=target,
        path_continuation=path_continuation,
        escalation_risk_score=risk_score,
        evidence_summary=f"Calculated transition graph for {incident.title}",
        limitations="Markov chain probability calculated from ATT&CK transition sequences; not a confirmed attacker action."
    )
    
    db.add(prediction)
    try:
        await db.commit()
    except IntegrityError:
        # A concurrent request persisted the same logical input first.
        await db.rollback()
        existing = await db.execute(
            select(Prediction).where(
                Prediction.incident_id == incident.id,
                Prediction.model_name == model_name,
                Prediction.model_version == model_version,
                Prediction.attack_version == attack_version,
                Prediction.input_fingerprint == fingerprint,
            )
        )
        return existing.scalars().one()
    await db.refresh(prediction)
    return prediction

@router.get("/{incident_id}/predictions/latest", response_model=PredictionResult)
async def get_latest_prediction(
    incident_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: Principal = Depends(require_permission(Permissions.PREDICTIONS_READ))
) -> Any:
    """
    Get the latest attack progression prediction for an incident.
    """
    result = await db.execute(
        select(Prediction)
        .where(Prediction.incident_id == incident_id)
        .order_by(Prediction.generated_at.desc())
        .limit(1)
    )
    prediction = result.scalars().first()
    
    if not prediction:
        # Fetch incident to compute initial prediction
        inc_result = await db.execute(select(Incident).where(Incident.id == incident_id))
        incident = inc_result.scalars().first()
        if not incident:
            raise HTTPException(status_code=404, detail="Incident not found.")
        prediction = await compute_and_save_prediction(incident, db)
        
    return PredictionResult(
        prediction_id=prediction.id,
        incident_id=prediction.incident_id,
        generated_at=prediction.generated_at,
        valid_until=prediction.valid_until,
        observed_techniques=prediction.observed_techniques,
        predicted_next_techniques=[TechniquePrediction(**t) for t in prediction.predicted_next_techniques],
        predicted_target=PredictionTarget(**prediction.predicted_target) if prediction.predicted_target else None,
        path_continuation=prediction.path_continuation,
        escalation_risk_score=prediction.escalation_risk_score,
        model_name=prediction.model_name,
        model_version=prediction.model_version,
        attack_version=prediction.attack_version,
        limitations=prediction.limitations
    )

@router.get("/{incident_id}/predictions", response_model=List[PredictionResult])
async def get_all_predictions(
    incident_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: Principal = Depends(require_permission(Permissions.PREDICTIONS_READ))
) -> Any:
    """
    Get all historical predictions for an incident.
    """
    result = await db.execute(
        select(Prediction)
        .where(Prediction.incident_id == incident_id)
        .order_by(Prediction.generated_at.desc())
    )
    predictions = result.scalars().all()
    
    return [
        PredictionResult(
            prediction_id=p.id,
            incident_id=p.incident_id,
            generated_at=p.generated_at,
            valid_until=p.valid_until,
            observed_techniques=p.observed_techniques,
            predicted_next_techniques=[TechniquePrediction(**t) for t in p.predicted_next_techniques],
            predicted_target=PredictionTarget(**p.predicted_target) if p.predicted_target else None,
            path_continuation=p.path_continuation,
            escalation_risk_score=p.escalation_risk_score,
            model_name=p.model_name,
            model_version=p.model_version,
            attack_version=p.attack_version,
            limitations=p.limitations
        ) for p in predictions
    ]

@router.post("/{incident_id}/predictions/recompute", status_code=202)
async def request_recompute(
    incident_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: Principal = Depends(require_permission(Permissions.PREDICTIONS_MANAGE))
) -> Any:
    """
    Request a recomputation of the attack progression prediction.
    """
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalars().first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found.")
        
    prediction = await compute_and_save_prediction(incident, db)
    return {
        "status": "accepted",
        "message": "Prediction recomputed successfully.",
        "prediction_id": str(prediction.id)
    }
