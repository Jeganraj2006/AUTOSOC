import pytest
import asyncio
from autosoc_correlation.main import CorrelationWorker

@pytest.mark.asyncio
async def test_worker_exposes_callable_run():
    worker = CorrelationWorker()
    assert hasattr(worker, "run"), "Worker must have a run method"
    assert callable(worker.run), "Worker's run attribute must be callable"

@pytest.mark.asyncio
async def test_worker_stop_is_safe_before_startup():
    worker = CorrelationWorker()
    await worker.stop()
    assert worker._running is False
