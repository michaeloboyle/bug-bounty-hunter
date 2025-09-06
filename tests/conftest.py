"""Test configuration and fixtures for bug bounty system tests."""

import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

# Import the FastAPI app
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'engine'))

from api.main import app

@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture
async def client():
    """HTTP client for testing API endpoints."""
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        yield ac

@pytest.fixture
def mock_socket():
    """Mock Socket.IO for testing real-time updates."""
    return AsyncMock()

@pytest.fixture
def sample_program():
    """Sample bug bounty program for testing."""
    return {
        "id": "test-program",
        "name": "Test Program",
        "platform": "H1",
        "payoutMax": 10000,
        "rps": 1.0,
        "autoOK": True,
        "triageDays": 7,
        "assetCount": 100,
        "tags": ["web", "api"]
    }

@pytest.fixture
def sample_finding():
    """Sample vulnerability finding for testing."""
    return {
        "id": "test-finding",
        "programId": "test-program",
        "type": "XSS",
        "severity": 7.5,
        "status": "needs_human",
        "payoutEst": 5000,
        "timestamp": datetime.now().isoformat(),
        "evidence": ["XSS payload proof", "Screenshot of execution"]
    }

@pytest.fixture
def sample_activity():
    """Sample activity for testing activity tracking."""
    return {
        "id": "test-activity",
        "type": "scan",
        "title": "Test Vulnerability Scan",
        "programId": "test-program",
        "triggeredBy": "automated",
        "status": "in_progress",
        "startTime": datetime.now().isoformat(),
        "artifacts": [],
        "runCount": 0
    }

@pytest.fixture(autouse=True)
def reset_test_data():
    """Reset global test data before each test."""
    from api.main import PROGRAMS, FINDINGS, SCAN_STATUSES, ACTIVITIES, ACTIVITY_RUNS, ACTIVITY_LOGS, ARTIFACTS
    
    # Clear all data structures
    PROGRAMS.clear()
    FINDINGS.clear()
    SCAN_STATUSES.clear()
    ACTIVITIES.clear()
    ACTIVITY_RUNS.clear()
    ACTIVITY_LOGS.clear()
    ARTIFACTS.clear()
    
    # Add default test data
    PROGRAMS.extend([
        {
            "id": "test-program-1",
            "name": "Test Program 1",
            "platform": "H1",
            "payoutMax": 10000,
            "rps": 1.0,
            "autoOK": True,
            "triageDays": 7,
            "assetCount": 100,
            "tags": ["web", "api"]
        },
        {
            "id": "test-program-2", 
            "name": "Test Program 2",
            "platform": "Bugcrowd",
            "payoutMax": 25000,
            "rps": 0.5,
            "autoOK": False,
            "triageDays": 14,
            "assetCount": 250,
            "tags": ["mobile", "cloud"]
        }
    ])
    
    yield