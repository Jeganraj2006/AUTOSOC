from datetime import datetime, timedelta, timezone

from autosoc_api.api.v1.endpoints.responses import (
    _TERMINAL_EXECUTION_STATUSES,
    approval_is_expired,
)


def test_approval_expiry_accepts_aware_postgresql_timestamp() -> None:
    """Regression: PostgreSQL-aware expiry must not raise during execution."""
    now = datetime(2026, 10, 26, 4, 0, tzinfo=timezone.utc)
    assert not approval_is_expired(now + timedelta(minutes=1), now)
    assert approval_is_expired(now - timedelta(minutes=1), now)


def test_approval_expiry_normalizes_legacy_naive_timestamp() -> None:
    """Legacy naive UTC rows remain comparable after the timezone repair."""
    now = datetime(2026, 10, 26, 4, 0, tzinfo=timezone.utc)
    assert not approval_is_expired(datetime(2026, 10, 26, 4, 1), now)
    assert approval_is_expired(datetime(2026, 10, 26, 3, 59), now)


def test_only_terminal_execution_states_are_idempotent_completion_hits() -> None:
    """Queued legacy rows must be recovered, not returned as completed work."""
    assert "succeeded" in _TERMINAL_EXECUTION_STATUSES
    assert "queued" not in _TERMINAL_EXECUTION_STATUSES
    assert "running" not in _TERMINAL_EXECUTION_STATUSES
