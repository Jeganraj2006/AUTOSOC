import asyncio
import uuid
import json
import httpx
from datetime import datetime, timezone
import random
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(PROJECT_ROOT / "workers" / "ingestion" / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "apps" / "api" / "src"))

from autosoc_api.db.session import AsyncSessionLocal
from autosoc_api.db.models.data_source import DataSource, DataSourceType, DataSourceHealth
from autosoc_api.db.models.incident import Incident, IncidentStatus
from autosoc_ingestion.services.auth import generate_api_key


async def create_source(db):
    source_id = str(uuid.uuid4())
    api_key, api_key_hash = generate_api_key()
    
    source = DataSource(
        id=source_id,
        name=f"Demo Source {random.randint(100, 999)}",
        source_type=DataSourceType.WINDOWS_EVENT,
        description="Demo source for Windows Event Logs",
        enabled=True,
        environment="production",
        api_key_hash=api_key_hash,
        health_state=DataSourceHealth.HEALTHY
    )
    db.add(source)
    await db.commit()
    return source_id, api_key

async def create_incident(db, title, desc, sev):
    inc = Incident(
        id=uuid.uuid4(),
        title=title,
        description=desc,
        severity=sev,
        status=IncidentStatus.NEW.value,
        risk_score=random.uniform(50, 95),
        alert_count=random.randint(1, 10),
        event_count=random.randint(50, 500),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(inc)
    await db.commit()

async def generate_events(count, source_id):
    event_types = ["login", "failed_login", "process_execution", "network_connection"]
    events = []
    for _ in range(count):
        evt_type = random.choice(event_types)
        event = {
            "synthetic_id": str(uuid.uuid4()),
            "type": evt_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source_ip": f"10.0.{random.randint(1, 255)}.{random.randint(1, 255)}",
            "user": f"user_{random.randint(1, 100)}",
            "message": f"Synthetic {evt_type} event generated for testing."
        }
        if evt_type == "process_execution":
            event["process"] = random.choice(["cmd.exe", "powershell.exe", "bash", "python"])
        elif evt_type == "network_connection":
            event["destination_port"] = random.choice([80, 443, 22, 3389])
        events.append(json.dumps(event))
    return events

async def main():
    print("Setting up demo data...")
    async with AsyncSessionLocal() as db:
        source_id, api_key = await create_source(db)
        print(f"Created Data Source: {source_id}")

        await create_incident(db, "Suspicious PowerShell Execution", "Detected encoded PowerShell command execution.", "high")
        await create_incident(db, "Multiple Failed Logins", "User account targeted with brute force.", "medium")
        await create_incident(db, "Lateral Movement Attempt", "SMB connection to multiple hosts.", "critical")
        print("Created mock incidents.")

    print("Generating and pushing synthetic events to ingestion API...")
    events = await generate_events(100, source_id)
    
    headers = {
        "X-Source-Id": source_id,
        "X-Api-Key": api_key,
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        batch_payload = {"events": events}
        try:
            resp = await client.post("http://127.0.0.1:8001/api/v1/ingest/events/batch", json=batch_payload, headers=headers)
            print(f"Batch ingestion response: {resp.status_code}")
            print(resp.text)
        except Exception as e:
            print(f"Failed to post to ingestion API: {e}. Is the backend running?")

if __name__ == "__main__":
    asyncio.run(main())
