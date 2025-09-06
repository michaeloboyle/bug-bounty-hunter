"""Tests for activity tracking system."""

import os
import sys
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

# Import activity tracking functions
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "engine"))

from api.main import (
    ACTIVITIES,
    ACTIVITY_LOGS,
    ACTIVITY_RUNS,
    ARTIFACTS,
    add_artifact,
    create_activity,
    create_activity_run,
    log_activity,
    update_activity_status,
)

class TestActivityTracking:
    """Test core activity tracking functionality."""

    def test_create_activity(self):
        """Test creating a new activity."""
        activity_id = create_activity(
            activity_type="scan",
            title="Test Vulnerability Scan",
            program_id="test-program",
            triggered_by="user",
        )

        assert activity_id is not None
        assert len(ACTIVITIES) == 1

        activity = ACTIVITIES[0]
        assert activity["id"] == activity_id
        assert activity["type"] == "scan"
        assert activity["title"] == "Test Vulnerability Scan"
        assert activity["programId"] == "test-program"
        assert activity["triggeredBy"] == "user"
        assert activity["status"] == "queued"
        assert activity["artifacts"] == []
        assert activity["runCount"] == 0

        # Check that related data structures are initialized
        assert activity_id in ACTIVITY_RUNS
        assert activity_id in ACTIVITY_LOGS
        assert ACTIVITY_RUNS[activity_id] == []
        assert ACTIVITY_LOGS[activity_id] == []

    def test_create_activity_run(self):
        """Test creating runs within an activity."""
        activity_id = create_activity("scan", "Test Scan")

        run_id = create_activity_run(activity_id, "reconnaissance", "Asset Discovery")

        assert run_id is not None
        assert len(ACTIVITY_RUNS[activity_id]) == 1

        run = ACTIVITY_RUNS[activity_id][0]
        assert run["id"] == run_id
        assert run["activityId"] == activity_id
        assert run["jobName"] == "reconnaissance"
        assert run["stepName"] == "Asset Discovery"
        assert run["status"] == "queued"

    def test_log_activity(self):
        """Test logging messages to activities."""
        activity_id = create_activity("scan", "Test Scan")

        log_activity(activity_id, "info", "Scan started")
        log_activity(activity_id, "error", "Network timeout")

        assert len(ACTIVITY_LOGS[activity_id]) == 2

        logs = ACTIVITY_LOGS[activity_id]
        assert logs[0]["level"] == "info"
        assert logs[0]["message"] == "Scan started"
        assert logs[1]["level"] == "error"
        assert logs[1]["message"] == "Network timeout"

        # Check timestamps are present
        assert "timestamp" in logs[0]
        assert "timestamp" in logs[1]

    def test_log_activity_with_run_context(self):
        """Test logging with run context."""
        activity_id = create_activity("scan", "Test Scan")
        run_id = create_activity_run(activity_id, "recon", "Discovery")

        log_activity(activity_id, "info", "Found 10 subdomains", run_id)

        logs = ACTIVITY_LOGS[activity_id]
        assert len(logs) == 1
        assert logs[0]["runId"] == run_id
        assert logs[0]["message"] == "Found 10 subdomains"

    def test_update_activity_status(self):
        """Test updating activity status and conclusion."""
        activity_id = create_activity("scan", "Test Scan")

        # Update to in_progress
        update_activity_status(activity_id, "in_progress")
        activity = next(a for a in ACTIVITIES if a["id"] == activity_id)
        assert activity["status"] == "in_progress"
        assert activity["endTime"] is None
        assert activity["duration"] is None

        # Update to completed with success
        update_activity_status(activity_id, "completed", "success")
        activity = next(a for a in ACTIVITIES if a["id"] == activity_id)
        assert activity["status"] == "completed"
        assert activity["conclusion"] == "success"
        assert activity["endTime"] is not None
        assert activity["duration"] is not None

    def test_add_artifact(self):
        """Test adding artifacts to activities."""
        activity_id = create_activity("scan", "Test Scan")
        run_id = create_activity_run(activity_id, "exploitation", "PoC Generation")

        add_artifact(
            activity_id,
            "vulnerability_report.md",
            "# Vulnerability Report\nFound XSS in search form",
            "text",
            run_id,
        )

        activity = next(a for a in ACTIVITIES if a["id"] == activity_id)
        assert len(activity["artifacts"]) == 1

        artifact_id = activity["artifacts"][0]
        assert artifact_id in ARTIFACTS

        artifact = ARTIFACTS[artifact_id]
        assert artifact["name"] == "vulnerability_report.md"
        assert artifact["type"] == "text"
        assert artifact["content"] == "# Vulnerability Report\nFound XSS in search form"
        assert artifact["runId"] == run_id
        assert artifact["size"] > 0

class TestActivityIntegration:
    """Test activity tracking integration with scan simulation."""

    @pytest.mark.asyncio
    async def test_scan_creates_activity(self):
        """Test that starting a scan creates proper activity tracking."""
        from api.main import SCAN_STATUSES, simulate_scan

        # Create a scan status
        scan_id = "test-scan-123"
        SCAN_STATUSES[scan_id] = {
            "id": scan_id,
            "programId": "test-program-1",
            "status": "queued",
            "progress": 0,
            "assetsFound": 0,
            "vulnerabilitiesFound": 0,
            "startTime": datetime.now().isoformat(),
        }

        # Mock socket.io to avoid actual emissions
        with patch("api.main.sio") as mock_sio:
            mock_sio.emit = AsyncMock()

            # Start scan simulation
            await simulate_scan(scan_id)

        # Verify activity was created
        assert len(ACTIVITIES) == 1
        activity = ACTIVITIES[0]
        assert activity["type"] == "scan"
        assert activity["programId"] == "test-program-1"
        assert activity["status"] == "completed"

        # Verify runs were created for each stage
        runs = ACTIVITY_RUNS[activity["id"]]
        assert len(runs) == 5  # recon, analysis, exploitation, reporting, completion

        job_names = [run["jobName"] for run in runs]
        assert "recon" in job_names
        assert "analysis" in job_names
        assert "exploitation" in job_names
        assert "reporting" in job_names
        assert "completion" in job_names

        # Verify logs were created
        logs = ACTIVITY_LOGS[activity["id"]]
        assert len(logs) > 0

        # Verify artifacts were created
        assert len(activity["artifacts"]) > 0
        assert activity["id"] in ARTIFACTS or any(
            aid in ARTIFACTS for aid in activity["artifacts"]
        )

    def test_activity_filtering_logic(self):
        """Test activity filtering functionality."""
        # Create activities of different types and statuses
        scan_id = create_activity("scan", "Test Scan", "program-1")
        submission_id = create_activity("submission", "Test Submission", "program-2")
        analysis_id = create_activity("analysis", "Test Analysis", "program-1")

        update_activity_status(scan_id, "completed", "success")
        update_activity_status(submission_id, "in_progress")
        update_activity_status(analysis_id, "failed", "failure")

        # Test type filtering
        scan_activities = [a for a in ACTIVITIES if a["type"] == "scan"]
        assert len(scan_activities) == 1
        assert scan_activities[0]["id"] == scan_id

        # Test status filtering
        completed_activities = [a for a in ACTIVITIES if a["status"] == "completed"]
        assert len(completed_activities) == 1
        assert completed_activities[0]["id"] == scan_id

        # Test program filtering
        program1_activities = [
            a for a in ACTIVITIES if a.get("programId") == "program-1"
        ]
        assert len(program1_activities) == 2

        # Test combined filtering
        program1_scans = [
            a
            for a in ACTIVITIES
            if a["type"] == "scan" and a.get("programId") == "program-1"
        ]
        assert len(program1_scans) == 1
        assert program1_scans[0]["id"] == scan_id