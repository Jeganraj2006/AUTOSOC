import asyncio
import json
import logging
import os
import uuid
from datetime import datetime, timezone

import httpx
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from autosoc_api.db.models.agent_execution import AgentExecution, AgentExecutionStatus
from autosoc_api.db.models.alert import Alert
from autosoc_api.db.models.incident import Incident
from autosoc_api.db.models.incident_alert import IncidentAlert
from autosoc_api.services.worker_reliability import RedisRetryState

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OLLAMA_URL = os.environ.get("OLLAMA_BASE_URL", "http://host.docker.internal:11434").rstrip("/")
OLLAMA_MODEL = os.environ.get("LLM_MODEL_NAME", "llama3.2:3b")


async def _incident_evidence(session: AsyncSession, incident: Incident) -> list[dict]:
    rows = await session.execute(
        select(Alert).join(IncidentAlert, IncidentAlert.alert_id == Alert.id).where(IncidentAlert.incident_id == incident.id)
    )
    return [
        {
            "alert_id": str(alert.id),
            "title": alert.title,
            "severity": str(alert.severity),
            "source_event_id": alert.source_event_id,
            "indicators": alert.indicators_json or {},
        }
        for alert in rows.scalars().all()
    ]


async def _run_local_inference(incident: Incident, evidence: list[dict]) -> str:
    """Return raw, bounded local-model output without inventing a fallback."""
    context = {
        "incident_id": str(incident.id),
        "title": incident.title,
        "severity": str(incident.severity),
        "description": incident.description,
        "primary_entities": incident.primary_entities or [],
        "candidate_mitre_references": incident.candidate_mitre_references or [],
        "alerts": evidence,
    }
    prompt = (
        "You are an AutoSOC investigation assistant. Use only this JSON evidence. "
        "Separate observed evidence, possible inferences, and analyst recommendations. "
        "Do not claim external intelligence lookups, do not give executable commands, "
        "and do not instruct automatic containment.\n\n" + json.dumps(context, default=str)
    )
    # Local CPU inference can legitimately exceed a short HTTP default.  Keep a
    # finite bound so the durable retry/DLQ path remains effective.
    async with httpx.AsyncClient(timeout=httpx.Timeout(180.0, connect=10.0)) as client:
        response = await client.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False, "options": {"temperature": 0.1, "num_predict": 250}},
        )
        response.raise_for_status()
        text = response.json().get("response", "").strip()
        if not text:
            raise RuntimeError("Ollama returned an empty investigation")
        return text


async def process_incident(session: AsyncSession, incident_id: str) -> bool:
    """Persist exactly one completed/failed investigation per incident lifecycle."""
    try:
        incident_uuid = uuid.UUID(incident_id)
    except ValueError:
        logger.error("Agent message has invalid incident_id: %r", incident_id)
        return False

    incident = await session.get(Incident, incident_uuid)
    if not incident:
        logger.error("Agent message references missing incident %s", incident_id)
        return False

    existing = await session.execute(
        select(AgentExecution).where(
            AgentExecution.incident_id == incident_uuid,
            AgentExecution.workflow_type == "incident_lifecycle_investigation",
        ).order_by(AgentExecution.created_at.desc()).limit(1)
    )
    execution = existing.scalars().first()
    if execution and execution.status == AgentExecutionStatus.COMPLETED:
        logger.info("Investigation already durable for incident %s", incident_id)
        return True
    if execution is None:
        execution = AgentExecution(
            incident_id=incident_uuid,
            workflow_type="incident_lifecycle_investigation",
            status=AgentExecutionStatus.QUEUED,
            requested_by="system:agent-worker",
            retry_count=0,
            node_statuses={"retrieving_incident_evidence": "queued", "local_ollama_inference": "queued"},
            node_timestamps={},
        )
        session.add(execution)
        await session.flush()

    started = datetime.now(timezone.utc)
    execution.status = AgentExecutionStatus.RUNNING
    execution.started_at = started
    execution.current_step = "retrieving_incident_evidence"
    execution.node_statuses = {
        **(execution.node_statuses or {}),
        "retrieving_incident_evidence": "running",
    }
    execution.node_timestamps = {
        **(execution.node_timestamps or {}),
        "retrieving_incident_evidence_started_at": started.isoformat(),
    }
    # Persist the ownership/status transition before model I/O. A timeout or
    # worker crash must leave a recoverable record rather than an invisible run.
    await session.commit()
    execution_id = execution.id
    try:
        evidence = await _incident_evidence(session, incident)
        execution.current_step = "local_ollama_inference"
        evidence_references = [item["alert_id"] for item in evidence]
        execution.evidence_references = evidence_references
        execution.node_statuses = {
            **(execution.node_statuses or {}),
            "retrieving_incident_evidence": "completed",
            "local_ollama_inference": "running",
        }
        execution.node_timestamps = {
            **(execution.node_timestamps or {}),
            "retrieving_incident_evidence_completed_at": datetime.now(timezone.utc).isoformat(),
            "local_ollama_inference_started_at": datetime.now(timezone.utc).isoformat(),
        }
        await session.commit()
        analysis = await _run_local_inference(incident, evidence)
        completed = datetime.now(timezone.utc)
        execution.status = AgentExecutionStatus.COMPLETED
        execution.completed_at = completed
        execution.current_step = "completed"
        execution.node_statuses = {
            **(execution.node_statuses or {}),
            "local_ollama_inference": "completed",
            "persistence": "completed",
        }
        execution.node_timestamps = {
            **(execution.node_timestamps or {}),
            "local_ollama_inference_completed_at": completed.isoformat(),
            "persistence_completed_at": completed.isoformat(),
        }
        execution.steps_completed = 7
        execution.tool_calls_count = 1
        execution.duration_seconds = max(1, int((completed - started).total_seconds()))
        execution.model_provider = "local Ollama"
        execution.model_name = OLLAMA_MODEL
        execution.model_version = "runtime"
        execution.prompt_version = "evidence-grounded-v1"
        execution.trace_id = f"agent-{execution.id}"
        execution.result_data = {
            "observed_evidence": evidence,
            "model_analysis": analysis,
            "inference_notice": "Advisory local-model output; analyst approval is required before any response action.",
            "response_proposals": [],
            "evidence_references": evidence_references,
        }
        await session.commit()
        logger.info("Persisted evidence-grounded investigation for incident %s", incident_id)
        return True
    except Exception as exc:
        await session.rollback()
        failed_execution = await session.get(AgentExecution, execution_id)
        if failed_execution is None:
            raise RuntimeError("Agent execution disappeared before failure could be recorded") from exc
        failed_step = failed_execution.current_step or "unknown"
        failed_execution.status = AgentExecutionStatus.FAILED
        failed_execution.retry_count = int(failed_execution.retry_count or 0) + 1
        failed_execution.completed_at = datetime.now(timezone.utc)
        failed_execution.failure_reason = f"{type(exc).__name__}: {exc}"[:4000]
        failed_execution.current_step = "failed"
        failed_execution.node_statuses = {
            **(failed_execution.node_statuses or {}),
            failed_step: "failed",
        }
        failed_execution.node_timestamps = {
            **(failed_execution.node_timestamps or {}),
            "failed_at": failed_execution.completed_at.isoformat(),
        }
        failed_execution.error_info = {
            "type": type(exc).__name__,
            "message": str(exc)[:1_000],
            "failed_at": failed_execution.completed_at.isoformat(),
        }
        await session.commit()
        logger.exception("Investigation failed for incident %s", incident_id)
        return False


async def main():
    logger.info("Starting AutoSOC Agent Worker incident consumer")
    engine = create_async_engine(os.environ["DATABASE_URL"], echo=False)
    sessions = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    consumer = AIOKafkaConsumer(
        os.environ.get("INCIDENTS_TOPIC", "security.incidents"),
        bootstrap_servers=os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "redpanda:9092"),
        group_id="autosoc-agent-worker-group",
        enable_auto_commit=False,
        auto_offset_reset="earliest",
        value_deserializer=lambda value: json.loads(value.decode("utf-8")),
    )
    producer = AIOKafkaProducer(
        bootstrap_servers=os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "redpanda:9092"),
        value_serializer=lambda value: json.dumps(value, default=str).encode("utf-8"),
    )
    retry_state = RedisRetryState(
        os.environ.get("REDIS_URL", "redis://redis:6379/4"),
        "agents",
        max_attempts=int(os.environ.get("RETRY_MAX_ATTEMPTS", "5")),
        base_delay_seconds=float(os.environ.get("RETRY_BASE_DELAY_SECONDS", "1")),
        max_delay_seconds=float(os.environ.get("RETRY_MAX_DELAY_SECONDS", "30")),
    )
    await consumer.start()
    await producer.start()
    try:
        async for message in consumer:
            incident_id = message.value.get("incident_id") if isinstance(message.value, dict) else None
            message_key = retry_state.message_key(message.topic, message.partition, message.offset)
            while True:
                async with sessions() as session:
                    durable = await process_incident(session, str(incident_id or ""))
                if durable:
                    await retry_state.acknowledge(message_key)
                    await consumer.commit()
                    break
                decision = await retry_state.record_failure(
                    message_key, RuntimeError("agent investigation was not durable")
                )
                if decision.exhausted:
                    try:
                        await producer.send_and_wait(
                            os.environ.get("FAILED_TOPIC", "security.events.failed"),
                            {
                                "failure_id": str(uuid.uuid4()),
                                "received_at": datetime.now(timezone.utc).isoformat(),
                                "failure_stage": "agent_investigation",
                                "failure_reason_code": "RETRY_EXHAUSTED",
                                "failure_description": "AI investigation failed after bounded retries",
                                "retryable": False,
                                "retry_count": decision.attempt,
                                "safe_metadata": {
                                    "topic": message.topic,
                                    "partition": message.partition,
                                    "offset": message.offset,
                                    "incident_id": str(incident_id or ""),
                                },
                            },
                        )
                    except Exception:
                        logger.exception("Agent DLQ publish failed; retaining Kafka offset")
                        await asyncio.sleep(decision.delay_seconds)
                        continue
                    await retry_state.acknowledge(message_key)
                    await consumer.commit()
                    logger.error("Retry exhausted for agent message %s", message_key)
                    break
                await asyncio.sleep(decision.delay_seconds)
    finally:
        await consumer.stop()
        await producer.stop()
        await retry_state.close()
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
