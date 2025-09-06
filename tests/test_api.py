"""Tests for FastAPI endpoints."""

import pytest
import json
from httpx import AsyncClient

class TestProgramsAPI:
    """Test program-related API endpoints."""
    
    async def test_get_programs(self, client: AsyncClient):
        """Test retrieving all programs."""
        response = await client.get("/programs")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 2  # From conftest.py fixtures
        assert data[0]["id"] == "test-program-1"
        assert data[1]["id"] == "test-program-2"

class TestScanAPI:
    """Test scan-related API endpoints."""
    
    async def test_queue_scan_success(self, client: AsyncClient):
        """Test successfully queueing a scan."""
        scan_request = {
            "program_id": "test-program-1",
            "priority": "fast_pay"
        }
        
        response = await client.post("/queue", json=scan_request)
        assert response.status_code == 200
        
        data = response.json()
        assert data["queued"] == True
        assert data["program_id"] == "test-program-1"
        assert data["priority"] == "fast_pay"
        assert "scan_id" in data

    async def test_queue_scan_invalid_program(self, client: AsyncClient):
        """Test queueing scan for non-existent program."""
        scan_request = {
            "program_id": "invalid-program",
            "priority": "fast_pay"
        }
        
        response = await client.post("/queue", json=scan_request)
        assert response.status_code == 404
        assert "Program not found" in response.json()["detail"]

    async def test_get_scan_statuses_empty(self, client: AsyncClient):
        """Test getting scan statuses when none exist."""
        response = await client.get("/scans")
        assert response.status_code == 200
        assert response.json() == []

class TestFindingsAPI:
    """Test findings-related API endpoints."""
    
    async def test_get_findings_empty(self, client: AsyncClient):
        """Test getting findings when none exist."""
        response = await client.get("/findings")
        assert response.status_code == 200
        assert response.json() == []

    async def test_get_findings_with_filter(self, client: AsyncClient):
        """Test filtering findings by status."""
        response = await client.get("/findings?status=needs_human")
        assert response.status_code == 200
        assert response.json() == []

    async def test_approve_finding_not_found(self, client: AsyncClient):
        """Test approving non-existent finding."""
        response = await client.post("/findings/invalid-id/approve")
        assert response.status_code == 404
        assert "Finding not found" in response.json()["detail"]

class TestActivityAPI:
    """Test activity tracking API endpoints."""
    
    async def test_get_activities_empty(self, client: AsyncClient):
        """Test getting activities when none exist."""
        response = await client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert data["activities"] == []
        assert data["total"] == 0
        assert data["hasMore"] == False

    async def test_get_activities_with_filters(self, client: AsyncClient):
        """Test filtering activities."""
        # Test activity_type filter
        response = await client.get("/activities?activity_type=scan")
        assert response.status_code == 200
        
        # Test status filter
        response = await client.get("/activities?status=completed")
        assert response.status_code == 200
        
        # Test program_id filter
        response = await client.get("/activities?program_id=test-program-1")
        assert response.status_code == 200

    async def test_get_activity_details_not_found(self, client: AsyncClient):
        """Test getting details for non-existent activity."""
        response = await client.get("/activities/invalid-id")
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    async def test_get_activity_logs_not_found(self, client: AsyncClient):
        """Test getting logs for non-existent activity."""
        response = await client.get("/activities/invalid-id/logs")
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    async def test_cancel_activity_not_found(self, client: AsyncClient):
        """Test cancelling non-existent activity."""
        response = await client.delete("/activities/invalid-id")
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

class TestAnalyticsAPI:
    """Test analytics API endpoints."""
    
    async def test_get_revenue_analytics(self, client: AsyncClient):
        """Test getting revenue analytics data."""
        response = await client.get("/analytics/revenue")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 5  # 5 months of sample data
        assert all("month" in item and "revenue" in item and "submissions" in item for item in data)

    async def test_get_vulnerability_analytics(self, client: AsyncClient):
        """Test getting vulnerability type analytics."""
        response = await client.get("/analytics/vulnerabilities")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 5  # 5 vulnerability types
        assert all("name" in item and "value" in item and "payout" in item for item in data)

class TestMCPEndpoints:
    """Test MCP-specific endpoints for Claude Code integration."""
    
    async def test_mcp_status(self, client: AsyncClient):
        """Test MCP status endpoint."""
        response = await client.get("/mcp/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "activeScans" in data
        assert "pendingReviews" in data
        assert "totalRevenue" in data
        assert "systemHealth" in data
        assert "lastUpdate" in data
        assert data["systemHealth"] == "operational"

    async def test_mcp_findings_summary(self, client: AsyncClient):
        """Test MCP findings summary endpoint."""
        response = await client.get("/mcp/findings/summary")
        assert response.status_code == 200
        
        data = response.json()
        assert "total" in data
        assert "byStatus" in data
        assert "byType" in data
        assert "totalValue" in data
        assert data["total"] == 0  # No findings in fresh test

    async def test_mcp_start_scan(self, client: AsyncClient):
        """Test MCP scan start endpoint."""
        response = await client.post("/mcp/scan/start?program_id=test-program-1&priority=high_ceiling")
        assert response.status_code == 200
        
        data = response.json()
        assert data["queued"] == True
        assert data["program_id"] == "test-program-1"
        assert data["priority"] == "high_ceiling"