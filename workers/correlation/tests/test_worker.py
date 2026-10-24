import pytest
import asyncio
from autosoc_correlation.main import app, CorrelationWorker

@pytest.mark.asyncio
async def test_worker_exposes_callable_run():
    worker = CorrelationWorker(app)
    assert hasattr(worker, "run"), "Worker must have a run method"
    assert callable(worker.run), "Worker's run attribute must be callable"

@pytest.mark.asyncio
async def test_worker_lifecycle():
    worker = CorrelationWorker(app)
    
    # Mock the FastKafka context manager so it doesn't connect to broker
    class MockApp:
        async def __aenter__(self): return self
        async def __aexit__(self, exc_type, exc_val, exc_tb): pass

    worker.app = MockApp()
    
    # Run the worker as a background task
    task = asyncio.create_task(worker.run())
    
    # Give it a moment to start
    await asyncio.sleep(0.1)
    
    # Assert it is running
    assert worker._running is True
    
    # Stop the worker
    await worker.stop()
    
    # Wait for the task to finish
    await task
    
    # Assert it stopped
    assert worker._running is False
