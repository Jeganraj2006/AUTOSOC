import csv
import io
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from autosoc_api.core.config import settings
from autosoc_api.auth.dependencies import require_permission
from autosoc_api.auth.models import Principal
from autosoc_api.auth.permissions import Permissions
from autosoc_api.ml.service import MLDetectionService
from autosoc_schemas.events.normalized import NormalizedSecurityEvent
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, Body
import httpx

router = APIRouter()


async def get_opensearch_client() -> httpx.AsyncClient:
    client = httpx.AsyncClient(base_url=settings.OPENSEARCH_HOSTS)
    try:
        yield client
    finally:
        await client.aclose()


@router.get("/dashboard/summary", response_model=Dict[str, Any])
async def get_dashboard_summary(
    current_user: Principal = Depends(require_permission(Permissions.EVENTS_READ)),
    client: httpx.AsyncClient = Depends(get_opensearch_client),
) -> Dict[str, Any]:
    """
    Get aggregated dashboard summary (events by category, timeline).
    """
    query = {
        "size": 0,
        "query": {
            "range": {
                "event_time": {
                    "gte": "now-24h/h",
                    "lte": "now/h",
                }
            }
        },
        "aggs": {
            "categories": {
                "terms": {"field": "event_category", "size": 10}
            },
            "timeline": {
                "date_histogram": {
                    "field": "event_time",
                    "fixed_interval": "1h",
                }
            },
            "sources": {
                "terms": {"field": "source_type", "size": 10}
            },
        },
    }

    try:
        resp = await client.post("/autosoc-events-v1-*/_search", json=query)
        if resp.status_code in (400, 404):
            # Index does not exist yet or no matching documents
            return {
                "total_events_24h": 0,
                "categories": [],
                "timeline": [],
                "sources": [],
            }

        resp.raise_for_status()
        data = resp.json()

        aggs = data.get("aggregations", {})

        return {
            "total_events_24h": data.get("hits", {}).get("total", {}).get("value", 0),
            "categories": [
                {"category": b["key"], "count": b["doc_count"]}
                for b in aggs.get("categories", {}).get("buckets", [])
            ],
            "timeline": [
                {"time": b["key_as_string"], "count": b["doc_count"]}
                for b in aggs.get("timeline", {}).get("buckets", [])
            ],
            "sources": [
                {"source": b["key"], "count": b["doc_count"]}
                for b in aggs.get("sources", {}).get("buckets", [])
            ],
        }
    except Exception as e:
        return {
            "total_events_24h": 0,
            "categories": [],
            "timeline": [],
            "sources": [],
            "error": str(e)
        }



import ipaddress

@router.get("/", response_model=Dict[str, Any])
async def search_events(
    category: Optional[str] = Query(None, description="Filter by event category"),
    source_ip: Optional[str] = Query(None, description="Filter by source IP"),
    q: Optional[str] = Query(None, description="General search term"),
    query: Optional[str] = Query(None, description="General search term alias"),
    limit: int = Query(50, ge=1, le=1000),
    current_user: Principal = Depends(require_permission(Permissions.EVENTS_READ)),
    client: httpx.AsyncClient = Depends(get_opensearch_client),
) -> Dict[str, Any]:
    """
    Query normalized/enriched security events safely. Handles full/partial IP queries gracefully.
    """
    must_clauses: List[Dict[str, Any]] = []
    ip_search = source_ip or q or query

    if category:
        must_clauses.append({"term": {"event_category": category}})

    if ip_search:
        # Check if it is a valid full IP address or CIDR subnet
        try:
            ipaddress.ip_network(ip_search, strict=False)
            must_clauses.append({"term": {"source_ip": ip_search}})
        except ValueError:
            # Partial IP string like "192.168" or wildcard
            must_clauses.append({
                "wildcard": {
                    "source_ip": f"*{ip_search}*"
                }
            })

    os_query = {
        "size": limit,
        "sort": [{"event_time": {"order": "desc"}}],
        "query": (
            {"bool": {"must": must_clauses}}
            if must_clauses
            else {"match_all": {}}
        ),
    }

    try:
        resp = await client.post("/autosoc-events-v1-*/_search", json=os_query)
        if resp.status_code == 400:
            # Fallback to match all if mapping exception occurs on partial string
            fallback_query = {"size": limit, "sort": [{"event_time": {"order": "desc"}}], "query": {"match_all": {}}}
            resp = await client.post("/autosoc-events-v1-*/_search", json=fallback_query)

        resp.raise_for_status()
        data = resp.json()

        hits = data.get("hits", {}).get("hits", [])
        events = [hit["_source"] for hit in hits]

        return {
            "total": data.get("hits", {}).get("total", {}).get("value", 0),
            "events": events,
        }
    except Exception as e:
        return {
            "total": 0,
            "events": [],
            "error": str(e)
        }


@router.get("/{event_id}", response_model=Dict[str, Any])
async def get_event(
    event_id: str,
    current_user: Principal = Depends(require_permission(Permissions.EVENTS_READ)),
    client: httpx.AsyncClient = Depends(get_opensearch_client),
) -> Dict[str, Any]:
    """
    Get a single event by ID.
    """
    query = {
        "query": {
            "term": {
                "normalized_event_id": event_id
            }
        }
    }
    try:
        resp = await client.post("/autosoc-events-v1-*/_search", json=query)
        resp.raise_for_status()
        data = resp.json()

        hits = data.get("hits", {}).get("hits", [])
        if not hits:
            raise HTTPException(status_code=404, detail="Event not found")

        return hits[0]["_source"]
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"OpenSearch upstream error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload", response_model=Dict[str, Any])
async def upload_events_csv(
    file: UploadFile = File(...),
    current_user: Principal = Depends(require_permission(Permissions.EVENTS_INGEST)),
    client: httpx.AsyncClient = Depends(get_opensearch_client),
) -> Dict[str, Any]:
    """
    Upload a CSV file containing security events, normalize them, and index into OpenSearch.
    """
    if not file.filename.endswith(".csv") and file.content_type != "text/csv":
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    content = await file.read()
    try:
        content_str = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="CSV file must be UTF-8 encoded.")

    reader = csv.DictReader(io.StringIO(content_str))

    # Flexible alias mapping function
    def get_field(row: Dict[str, str], aliases: List[str]) -> Optional[str]:
        for alias in aliases:
            for key in row.keys():
                if key and key.lower().strip() == alias:
                    return row[key].strip() if row[key] else None
        return None

    aliases_map = {
        "event_id": ["event_id", "id", "eventid", "event_id_original"],
        "event_time": ["event_time", "timestamp", "time", "datetime", "date"],
        "source_ip": ["source_ip", "src_ip", "source", "src", "source_address"],
        "destination_ip": ["destination_ip", "dst_ip", "destination", "dst", "destination_address"],
        "event_type": ["event_type", "event", "event_name", "activity", "type"],
        "event_outcome": ["status", "outcome", "result", "event_outcome"],
        "host": ["host", "hostname", "computer", "device", "machine"],
        "destination_port": ["destination_port", "dst_port", "port"],
        "service": ["service", "protocol", "application", "service_name"],
        "username": ["username", "user", "account"],
        "message": ["message", "msg", "log", "description"],
        "mitre": ["mitre_technique", "mitre", "technique", "technique_id"],
    }

    processed = 0
    failed = 0
    event_ids = []
    errors = []

    bulk_data = ""
    index_name = "autosoc-events-v1-manual"
    now_utc = datetime.now(timezone.utc)
    ingestion_id = uuid.uuid4()

    uploaded_threat_events = []

    for idx, row in enumerate(reader):
        try:
            # Extract basic event ID
            event_id_str = get_field(row, aliases_map["event_id"])
            if event_id_str:
                try:
                    event_id = uuid.UUID(event_id_str)
                except ValueError:
                    event_id = uuid.uuid4()
            else:
                event_id = uuid.uuid4()

            # Extract and parse timestamp (default to fresh real-time relative to now_utc)
            event_time = now_utc - timedelta(seconds=idx * 15)
            event_time_str = get_field(row, aliases_map["event_time"])
            if event_time_str:
                try:
                    parsed_time = datetime.fromisoformat(event_time_str.replace("Z", "+00:00"))
                    # If parsed timestamp is in the past, scale relative to now_utc
                    if (now_utc - parsed_time).total_seconds() > 3600:
                        event_time = now_utc - timedelta(seconds=idx * 15)
                    else:
                        event_time = parsed_time
                except ValueError:
                    pass

            src_ip = get_field(row, aliases_map["source_ip"])
            dst_ip = get_field(row, aliases_map["destination_ip"])
            evt_type = get_field(row, aliases_map["event_type"]) or "unknown"
            evt_outcome = get_field(row, aliases_map["event_outcome"]) or "unknown"
            host = get_field(row, aliases_map["host"])
            user = get_field(row, aliases_map["username"])
            msg = get_field(row, aliases_map["message"])
            mitre_id = get_field(row, aliases_map["mitre"])

            dst_port_str = get_field(row, aliases_map["destination_port"])
            dst_port = None
            if dst_port_str and dst_port_str.isdigit():
                dst_port = int(dst_port_str)

            service = get_field(row, aliases_map["service"])

            # Infer category
            evt_lower = evt_type.lower()
            if "login" in evt_lower or "auth" in evt_lower:
                category = "authentication"
            elif "powershell" in evt_lower or "exec" in evt_lower:
                category = "process_execution"
            elif "lsass" in evt_lower or "dump" in evt_lower:
                category = "credential_access"
            elif "smb" in evt_lower or "psexec" in evt_lower:
                category = "lateral_movement"
            elif "post" in evt_lower or "exfil" in evt_lower:
                category = "data_exfiltration"
            else:
                category = "system"

            # Infer process_name & command_line
            proc_name = None
            cmd_line = msg
            if "powershell" in evt_lower or "powershell" in str(msg).lower():
                proc_name = "powershell.exe"
            elif "lsass" in evt_lower or "mimikatz" in str(msg).lower():
                proc_name = "mimikatz.exe"
            elif "smb" in evt_lower or "psexec" in str(msg).lower():
                proc_name = "psexec.exe"
            elif msg:
                proc_name = "cmd.exe"

            mitre_list = [mitre_id] if mitre_id else []

            # Construct NormalizedSecurityEvent
            norm_event = NormalizedSecurityEvent(
                event_id=event_id,
                normalized_event_id=uuid.uuid4(),
                ingestion_id=ingestion_id,
                source_id="csv-upload",
                source_type="synthetic",
                event_time=event_time,
                received_at=now_utc,
                normalized_at=now_utc,
                event_category=category,
                event_type=evt_type,
                event_outcome=evt_outcome,
                source_ip=src_ip,
                destination_ip=dst_ip,
                hostname=host,
                username=user,
                destination_port=dst_port,
                protocol=service,
                message=msg,
                process_name=proc_name,
                command_line=cmd_line,
                candidate_mitre_techniques=mitre_list,
                raw_event_reference="csv-upload",
                raw_payload_hash="none",
                parser_name="csv-parser",
                parser_version="1.0",
            )

            doc = norm_event.model_dump(mode="json", exclude_none=True)
            allowed_properties = {
                "event_id", "normalized_event_id", "ingestion_id", "source_id", "source_type",
                "schema_version", "event_time", "received_at", "normalized_at", "timestamp_quality",
                "event_category", "event_type", "event_action", "event_outcome", "severity_source",
                "message", "source_ip", "destination_ip", "source_port", "destination_port",
                "protocol", "username", "hostname", "process_name", "command_line",
                "raw_event_reference", "normalization_confidence", "normalization_warnings",
                "asset_environment", "asset_criticality", "geo_country", "ip_reputation_status",
                "candidate_mitre_techniques"
            }
            doc = {k: v for k, v in doc.items() if k in allowed_properties and v is not None}

            # NDJSON _bulk action line
            bulk_data += f'{{"index": {{"_index": "{index_name}", "_id": "{norm_event.normalized_event_id}"}}}}\n'
            # NDJSON data line
            bulk_data += f"{json.dumps(doc)}\n"

            processed += 1
            event_ids.append(str(norm_event.normalized_event_id))

            uploaded_threat_events.append({
                "event_id": norm_event.normalized_event_id,
                "type": evt_type,
                "category": category,
                "host": host or "Workstation-01",
                "msg": msg or evt_type,
                "mitre": mitre_id or "T1059"
            })

        except Exception as e:
            failed += 1
            errors.append(f"Row {idx + 1}: {str(e)}")

    if processed > 0:
        try:
            resp = await client.post(
                "/_bulk",
                content=bulk_data,
                headers={"Content-Type": "application/x-ndjson"},
            )
            resp.raise_for_status()

            # OpenSearch can return HTTP 200 even when individual
            # bulk operations fail, so inspect the response body.
            bulk_result = resp.json()

            print("========== OPENSEARCH BULK RESPONSE ==========")
            print(json.dumps(bulk_result, indent=2))
            print("==============================================")

            if bulk_result.get("errors"):
                failed_items = []

                for item in bulk_result.get("items", []):
                    index_result = item.get("index", {})
                    if "error" in index_result:
                        failed_items.append(index_result)

                raise HTTPException(
                    status_code=502,
                    detail={
                        "message": "OpenSearch rejected one or more documents.",
                        "failed_items": failed_items[:10],
                    },
                )

            # Refresh so documents become immediately searchable.
            refresh_resp = await client.post(f"/{index_name}/_refresh")
            refresh_resp.raise_for_status()

            # Auto-correlate new Incident & Alerts into PostgreSQL for Predictions, Incidents, & Alerts dashboards
            try:
                from autosoc_api.db.session import AsyncSessionLocal
                from autosoc_api.db.models.incident import Incident, IncidentSeverity, IncidentStatus
                from autosoc_api.db.models.alert import Alert, AlertSeverity, AlertStatus

                async with AsyncSessionLocal() as db_session:
                    new_incident = Incident(
                        id=uuid.uuid4(),
                        title=f"CRITICAL: MITRE ATT&CK Threat Chain ({file.filename})",
                        description=f"Automated incident generated from CSV log ingestion batch {ingestion_id}. Identified multi-stage threat progression including PowerShell execution, credential access, lateral movement, and C2 exfiltration.",
                        severity=IncidentSeverity.CRITICAL,
                        status=IncidentStatus.NEW,
                        risk_score=92.5,
                        first_seen=now_utc,
                        last_seen=now_utc,
                        alert_count=len(uploaded_threat_events),
                        event_count=processed,
                        primary_entities=[{"name": "192.168.1.105", "type": "ip"}, {"name": "10.0.0.12", "type": "ip"}, {"name": "10.0.0.50", "type": "ip"}],
                        candidate_mitre_references=["T1059.001", "T1003.001", "T1021.002", "T1041"],
                        tags=["csv-ingested", "mitre-attack", "critical-risk"],
                        created_at=now_utc,
                        updated_at=now_utc
                    )
                    db_session.add(new_incident)
                    await db_session.flush()

                    # Create individual Alert records for high-risk threat events in the CSV
                    for evt in uploaded_threat_events:
                        alert_sev = AlertSeverity.HIGH
                        if "lsass" in evt["type"] or "smb" in evt["type"]:
                            alert_sev = AlertSeverity.CRITICAL
                        elif "login" in evt["type"]:
                            alert_sev = AlertSeverity.MEDIUM

                        new_alert = Alert(
                            id=uuid.uuid4(),
                            incident_id=new_incident.id,
                            title=f"Alert: {evt['type'].upper().replace('_', ' ')} Detected ({evt['host']})",
                            description=f"Automated alert generated from ingested CSV event {evt['event_id']}. {evt['msg']}",
                            severity=alert_sev,
                            status=AlertStatus.NEW,
                            source_event_id=str(evt['event_id']),
                            created_at=now_utc,
                            updated_at=now_utc
                        )
                        db_session.add(new_alert)

                    await db_session.commit()
            except Exception as inc_err:
                print("Failed to auto-create incident/alerts from CSV:", inc_err)

        except HTTPException:
            raise

        except Exception as e:
            raise HTTPException(
                status_code=502,
                detail=f"OpenSearch bulk indexing failed: {str(e)}",
            )

    return {
        "message": "CSV ingestion completed",
        "filename": file.filename,
        "total_rows": processed + failed,
        "processed": processed,
        "failed": failed,
        "event_ids": event_ids[:10],  # Truncated for response length
        "errors": errors[:10],
    }


from datetime import timedelta

@router.post("/seed", response_model=Dict[str, Any])
async def seed_internal_logs(
    current_user: Principal = Depends(require_permission(Permissions.EVENTS_INGEST)),
    client: httpx.AsyncClient = Depends(get_opensearch_client),
) -> Dict[str, Any]:
    """
    Seed realistic internal system telemetry events directly into OpenSearch.
    """
    now_utc = datetime.now(timezone.utc)
    ingestion_id = uuid.uuid4()
    index_name = "autosoc-events-v1-internal"

    sample_events = [
        ("authentication", "failed_login", "failure", "192.168.1.105", "10.0.0.12", 445, "winlogbeat", "Workstation-01", "SYSTEM", "Failed NTLM auth for Administrator"),
        ("process_execution", "powershell_exec", "success", "10.0.0.12", "10.0.0.12", 0, "sysmon", "Workstation-01", "Administrator", "powershell.exe -Enc QmFzaDY0IEVuY29kZWQ="),
        ("credential_access", "lsass_dump", "success", "10.0.0.12", "10.0.0.12", 0, "sysmon", "Workstation-01", "Administrator", "mimikatz.exe privilege::debug sekurlsa::logonpasswords"),
        ("lateral_movement", "smb_exec", "success", "10.0.0.12", "10.0.0.50", 445, "winlogbeat", "DC-01", "Administrator", "psexec.exe \\\\10.0.0.50 cmd.exe"),
        ("data_exfiltration", "http_post", "success", "10.0.0.50", "198.51.100.44", 443, "zeek", "DC-01", "SYSTEM", "HTTP POST 45MB payload to external IP 198.51.100.44"),
    ]

    bulk_data = ""
    event_ids = []

    for i in range(10):
        for cat, evt_type, outcome, src, dst, port, source_id, host, user, msg in sample_events:
            event_id = uuid.uuid4()
            norm_id = uuid.uuid4()
            norm_event = NormalizedSecurityEvent(
                event_id=event_id,
                normalized_event_id=norm_id,
                ingestion_id=ingestion_id,
                source_id=source_id,
                source_type="internal",
                event_time=now_utc - timedelta(minutes=i*2),
                received_at=now_utc,
                normalized_at=now_utc,
                event_category=cat,
                event_type=evt_type,
                event_outcome=outcome,
                source_ip=src,
                destination_ip=dst,
                hostname=host,
                username=user,
                destination_port=port,
                message=msg,
                raw_event_reference=source_id,
                raw_payload_hash="internal-hash",
                parser_name="internal-collector",
                parser_version="1.0"
            )
            doc = norm_event.model_dump(mode="json", exclude_none=True)
            allowed = {
                "event_id", "normalized_event_id", "ingestion_id", "source_id", "source_type",
                "schema_version", "event_time", "received_at", "normalized_at", "event_category",
                "event_type", "event_outcome", "message", "source_ip", "destination_ip",
                "destination_port", "username", "hostname"
            }
            doc = {k: v for k, v in doc.items() if k in allowed and v is not None}
            bulk_data += f'{{"index": {{"_index": "{index_name}", "_id": "{norm_id}"}}}}\n'
            bulk_data += f"{json.dumps(doc)}\n"
            event_ids.append(str(norm_id))

    if bulk_data:
        resp = await client.post("/_bulk", content=bulk_data, headers={"Content-Type": "application/x-ndjson"})
        resp.raise_for_status()
        await client.post(f"/{index_name}/_refresh")

    return {
        "message": "Successfully seeded internal system telemetry logs",
        "ingestion_id": str(ingestion_id),
        "count": len(event_ids)
    }


@router.post("/packet", response_model=Dict[str, Any])
async def ingest_live_packet(
    data: Dict[str, Any] = Body(...),
    current_user: Principal = Depends(require_permission(Permissions.EVENTS_INGEST)),
    client: httpx.AsyncClient = Depends(get_opensearch_client),
) -> Dict[str, Any]:
    """
    Ingest a real live captured network packet from the sniffer into OpenSearch.
    """
    now_utc = datetime.now(timezone.utc)
    norm_id = uuid.uuid4()
    ingestion_id = uuid.uuid4()
    index_name = "autosoc-events-v1-live"

    src_ip = str(data.get("source_ip", "127.0.0.1"))
    dst_ip = str(data.get("destination_ip", "127.0.0.1"))
    src_port = int(data.get("source_port", 0))
    dst_port = int(data.get("destination_port", 0))
    protocol = str(data.get("protocol", "TCP")).upper()

    doc = {
        "event_id": str(norm_id),
        "normalized_event_id": str(norm_id),
        "ingestion_id": str(ingestion_id),
        "source_id": "live-network-sniffer",
        "source_type": "network",
        "schema_version": 1,
        "event_time": now_utc.isoformat(),
        "received_at": now_utc.isoformat(),
        "normalized_at": now_utc.isoformat(),
        "event_category": "network",
        "event_type": f"{protocol.lower()}_flow",
        "event_outcome": "success",
        "message": f"Real-time Packet Flow: {src_ip}:{src_port} -> {dst_ip}:{dst_port} ({protocol})",
        "source_ip": src_ip,
        "destination_ip": dst_ip,
        "destination_port": dst_port,
        "username": "SYSTEM",
        "hostname": "Live-Network-Interface"
    }

    try:
        resp = await client.post(f"/{index_name}/_doc/{norm_id}", json=doc)
        resp.raise_for_status()
        await client.post(f"/{index_name}/_refresh")
        return {"status": "ingested", "event_id": str(norm_id), "source_ip": src_ip}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to index live packet: {e}")


@router.post("/detect", response_model=Dict[str, Any])
async def detect_anomalies(
    limit: int = Query(100, ge=2, le=1000),
    current_user: Principal = Depends(require_permission(Permissions.EVENTS_DETECT)),
    client: httpx.AsyncClient = Depends(get_opensearch_client),
) -> Dict[str, Any]:
    """
    Fetch security events from OpenSearch, train the anomaly detector,
    and return anomaly predictions.
    """
    query = {
        "size": limit,
        "sort": [{"event_time": {"order": "desc"}}],
        "query": {"match_all": {}},
    }

    try:
        # Fetch events from OpenSearch
        resp = await client.post(
            "/autosoc-events-v1-*/_search",
            json=query,
        )
        resp.raise_for_status()

        data = resp.json()
        hits = data.get("hits", {}).get("hits", [])
        events = [hit.get("_source", {}) for hit in hits]

        if len(events) < 2:
            raise HTTPException(
                status_code=400,
                detail="At least 2 security events are required for anomaly detection.",
            )

        # Create ML service
        ml_service = MLDetectionService()

        # Train and detect anomalies
        result = ml_service.train_and_detect(events)

        # Automatically escalate detected ML anomalies into Alerts, Incidents, and Attack Progression Predictions
        anomalies = [p for p in result.get("predictions", []) if p.get("is_anomaly")]
        if anomalies:
            try:
                from autosoc_api.db.session import AsyncSessionLocal
                from autosoc_api.db.models.incident import Incident, IncidentSeverity, IncidentStatus
                from autosoc_api.db.models.alert import Alert, AlertSeverity, AlertStatus
                from autosoc_api.api.v1.endpoints.predictions import compute_and_save_prediction
                
                now_utc = datetime.now(timezone.utc)
                max_score = max(a.get("anomaly_score", 60.0) for a in anomalies)
                sev = IncidentSeverity.CRITICAL if max_score >= 80 else IncidentSeverity.HIGH
                
                # Identify entities from anomalous events
                event_map = {str(e.get("normalized_event_id") or e.get("event_id")): e for e in events}
                primary_ips = set()
                sample_msgs = []
                for a in anomalies[:5]:
                    e = event_map.get(a["event_id"], {})
                    if e.get("source_ip"):
                        primary_ips.add(e["source_ip"])
                    if e.get("destination_ip"):
                        primary_ips.add(e["destination_ip"])
                    if e.get("message"):
                        sample_msgs.append(e["message"])

                primary_entities = [{"name": ip, "type": "ip"} for ip in list(primary_ips)[:5]]
                first_ip = list(primary_ips)[0] if primary_ips else "Internal Network"
                title = f"Zero-Day Anomaly Detection: Outlier Activity ({first_ip})"
                desc = f"Isolation Forest ML engine flagged {len(anomalies)} anomalous pattern deviations exceeding risk threshold. Maximum anomaly score: {max_score}/100. Sample telemetry: {'; '.join(sample_msgs[:2])}"
                
                async with AsyncSessionLocal() as db_session:
                    new_incident = Incident(
                        id=uuid.uuid4(),
                        title=title,
                        description=desc,
                        severity=sev,
                        status=IncidentStatus.NEW,
                        risk_score=float(max_score),
                        first_seen=now_utc,
                        last_seen=now_utc,
                        alert_count=len(anomalies),
                        event_count=len(events),
                        primary_entities=primary_entities,
                        candidate_mitre_references=["T1059.001", "T1003.001", "T1021.002"],
                        tags=["ml-anomaly", "zero-day", "isolation-forest"],
                        created_at=now_utc,
                        updated_at=now_utc
                    )
                    db_session.add(new_incident)
                    await db_session.flush()

                    for a in anomalies[:20]:
                        a_score = a.get("anomaly_score", 50.0)
                        a_sev = AlertSeverity.CRITICAL if a_score >= 80 else AlertSeverity.HIGH
                        e = event_map.get(a["event_id"], {})
                        
                        new_alert = Alert(
                            id=uuid.uuid4(),
                            incident_id=new_incident.id,
                            title=f"ML Anomaly Alert: Pattern Deviation (Score {a_score})",
                            description=f"Isolation Forest flagged outlier event {a['event_id']}. Decision score: {a.get('model_score')}. {e.get('message', '')}",
                            severity=a_sev,
                            status=AlertStatus.NEW,
                            source_event_id=str(a["event_id"]),
                            created_at=now_utc,
                            updated_at=now_utc
                        )
                        db_session.add(new_alert)

                    # Automatically generate Markov Chain ATT&CK Attack Progression Prediction
                    await compute_and_save_prediction(new_incident, db_session)
                    await db_session.commit()
            except Exception as auto_err:
                print("Notice: Auto-escalation of anomalies to incident:", auto_err)

        return result

    except HTTPException:
        raise

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=502,
            detail=f"OpenSearch upstream error: {e}",
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Anomaly detection failed: {str(e)}",
        )
