from datetime import datetime, timezone

from autosoc_api.api.v1.endpoints.audit import redact_metadata
from autosoc_api.api.v1.endpoints.events import build_event_search_query
from autosoc_api.api.v1.endpoints.incidents import get_incident_alerts
from autosoc_api.db.models.alert import Alert


class _ScalarRows:
    def __init__(self, values):
        self.values = values

    def all(self):
        return self.values


class _Result:
    def __init__(self, values):
        self.values = values

    def scalars(self):
        return _ScalarRows(self.values)


class _Session:
    def __init__(self, values):
        self.values = values
        self.statement = None

    async def execute(self, statement):
        self.statement = statement
        return _Result(self.values)


def test_event_search_query_uses_stable_server_paging_and_filters() -> None:
    query = build_event_search_query(
        category="process_execution",
        source_id="sysmon",
        severity="high",
        source_ip="10.0.0.1",
        destination_ip="10.0.0.2",
        file_hash="a" * 64,
        text_query="powershell suspicious",
        start_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
        end_time=datetime(2026, 1, 2, tzinfo=timezone.utc),
        limit=50,
        offset=100,
        sort_field="event_time",
        sort_direction="desc",
    )

    assert query["from"] == 100
    assert query["size"] == 50
    assert query["track_total_hits"] is True
    assert query["sort"][-1] == {"_id": {"order": "desc"}}
    assert {"term": {"event_category": "process_execution"}} in query["query"]["bool"]["filter"]
    assert {"term": {"source_id": "sysmon"}} in query["query"]["bool"]["filter"]
    assert {"term": {"severity_source": "high"}} in query["query"]["bool"]["filter"]
    search_clause = query["query"]["bool"]["must"][0]["bool"]
    assert search_clause["should"][0]["simple_query_string"]["query"] == "powershell suspicious"
    assert search_clause["should"][1]["wildcard"]["message"]["value"] == "*powershell suspicious*"


def test_event_search_escapes_user_wildcards() -> None:
    query = build_event_search_query(
        category=None,
        source_id=None,
        severity=None,
        source_ip=None,
        destination_ip=None,
        file_hash=None,
        text_query="literal*?query",
        start_time=None,
        end_time=None,
        limit=1,
        offset=0,
        sort_field="event_time",
        sort_direction="desc",
    )
    value = query["query"]["bool"]["must"][0]["bool"]["should"][1]["wildcard"]["message"]["value"]
    assert value == r"*literal\*\?query*"


def test_audit_metadata_redaction_handles_nested_sensitive_values() -> None:
    metadata = {
        "request": {"authorization": "Bearer never-return-this", "safe": "visible"},
        "items": [{"api_key": "hidden"}, {"result": "kept"}],
    }

    assert redact_metadata(metadata) == {
        "request": {"authorization": "[REDACTED]", "safe": "visible"},
        "items": [{"api_key": "[REDACTED]"}, {"result": "kept"}],
    }


def test_incident_alerts_reads_durable_evidence_links() -> None:
    import asyncio
    import uuid

    sentinel = object()
    session = _Session([sentinel])
    assert asyncio.run(get_incident_alerts(uuid.uuid4(), db=session, current_user=None)) == [sentinel]

    compiled = str(session.statement.compile(compile_kwargs={"literal_binds": True}))
    assert "JOIN incident_alerts" in compiled
    assert "WHERE incident_alerts.incident_id" in compiled
