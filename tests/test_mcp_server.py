"""Tests for MCP server functionality."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import json

# Import MCP server components
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'engine'))

from mcp_server import BugBountyOpsClient, server

class TestBugBountyOpsClient:
    """Test the MCP client for API communication."""
    
    @pytest.mark.asyncio
    async def test_client_get_request(self):
        """Test GET requests to the API."""
        client = BugBountyOpsClient("http://test-api")
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = {"test": "data"}
            mock_response.raise_for_status.return_value = None
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            result = await client.get("/test-endpoint")
            
            assert result == {"test": "data"}
            mock_client.return_value.__aenter__.return_value.get.assert_called_once_with("http://test-api/test-endpoint")

    @pytest.mark.asyncio
    async def test_client_post_request(self):
        """Test POST requests to the API."""
        client = BugBountyOpsClient("http://test-api")
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = {"success": True}
            mock_response.raise_for_status.return_value = None
            
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            
            result = await client.post("/test-endpoint", {"key": "value"})
            
            assert result == {"success": True}
            mock_client.return_value.__aenter__.return_value.post.assert_called_once_with(
                "http://test-api/test-endpoint", 
                json={"key": "value"}
            )

class TestMCPServerResources:
    """Test MCP server resource endpoints."""
    
    @pytest.mark.asyncio
    async def test_list_resources(self):
        """Test listing available MCP resources."""
        resources = await server.list_resources()
        
        assert len(resources) == 5
        resource_uris = [r.uri for r in resources]
        
        expected_uris = [
            "bugbounty://status",
            "bugbounty://programs", 
            "bugbounty://findings",
            "bugbounty://scans",
            "bugbounty://analytics"
        ]
        
        for uri in expected_uris:
            assert uri in resource_uris

    @pytest.mark.asyncio  
    async def test_read_status_resource(self):
        """Test reading the status resource."""
        with patch('mcp_server.bb_client.get') as mock_get:
            mock_get.return_value = {
                "activeScans": 2,
                "pendingReviews": 3,
                "totalRevenue": 50000,
                "systemHealth": "operational"
            }
            
            result = await server.read_resource("bugbounty://status")
            
            data = json.loads(result)
            assert data["activeScans"] == 2
            assert data["systemHealth"] == "operational"
            mock_get.assert_called_once_with("/mcp/status")

    @pytest.mark.asyncio
    async def test_read_programs_resource(self):
        """Test reading the programs resource.""" 
        with patch('mcp_server.bb_client.get') as mock_get:
            mock_get.return_value = [
                {"id": "program1", "name": "Test Program 1"},
                {"id": "program2", "name": "Test Program 2"}
            ]
            
            result = await server.read_resource("bugbounty://programs")
            
            data = json.loads(result)
            assert len(data) == 2
            assert data[0]["name"] == "Test Program 1"
            mock_get.assert_called_once_with("/programs")

    @pytest.mark.asyncio
    async def test_read_findings_resource(self):
        """Test reading the findings resource with summary."""
        with patch('mcp_server.bb_client.get') as mock_get:
            mock_get.side_effect = [
                [{"id": "f1", "type": "XSS"}, {"id": "f2", "type": "SSRF"}],  # /findings
                {"total": 2, "byStatus": {"needs_human": 1}, "byType": {"XSS": 1}}  # /mcp/findings/summary
            ]
            
            result = await server.read_resource("bugbounty://findings")
            
            data = json.loads(result)
            assert "summary" in data
            assert "findings" in data
            assert data["summary"]["total"] == 2
            assert len(data["findings"]) == 2

    @pytest.mark.asyncio
    async def test_read_unknown_resource(self):
        """Test reading an unknown resource."""
        result = await server.read_resource("bugbounty://unknown")
        
        data = json.loads(result)
        assert "error" in data
        assert "Unknown resource" in data["error"]

class TestMCPServerTools:
    """Test MCP server tool endpoints."""
    
    @pytest.mark.asyncio
    async def test_list_tools(self):
        """Test listing available MCP tools."""
        tools = await server.list_tools()
        
        assert len(tools) == 5
        tool_names = [t.name for t in tools]
        
        expected_tools = [
            "start_scan",
            "approve_finding", 
            "stop_scan",
            "get_system_health",
            "analyze_finding"
        ]
        
        for tool_name in expected_tools:
            assert tool_name in tool_names

    @pytest.mark.asyncio
    async def test_start_scan_tool(self):
        """Test the start_scan tool."""
        with patch('mcp_server.bb_client.post') as mock_post:
            mock_post.return_value = {
                "queued": True,
                "scan_id": "scan-123",
                "program_id": "test-program",
                "priority": "fast_pay"
            }
            
            result = await server.call_tool("start_scan", {
                "program_id": "test-program",
                "priority": "fast_pay"
            })
            
            assert len(result) == 1
            assert "✅ Scan started for program test-program" in result[0].text
            assert "scan-123" in result[0].text
            
            mock_post.assert_called_once_with("/queue", {
                "program_id": "test-program",
                "priority": "fast_pay"
            })

    @pytest.mark.asyncio
    async def test_approve_finding_tool(self):
        """Test the approve_finding tool."""
        with patch('mcp_server.bb_client.post') as mock_post:
            mock_post.return_value = {"approved": True, "finding_id": "f1"}
            
            result = await server.call_tool("approve_finding", {
                "finding_id": "f1"
            })
            
            assert len(result) == 1
            assert "✅ Finding f1 has been approved" in result[0].text
            
            mock_post.assert_called_once_with("/findings/f1/approve")

    @pytest.mark.asyncio
    async def test_stop_scan_tool(self):
        """Test the stop_scan tool.""" 
        with patch('mcp_server.bb_client.delete') as mock_delete:
            mock_delete.return_value = {"stopped": True, "scan_id": "scan-123"}
            
            result = await server.call_tool("stop_scan", {
                "scan_id": "scan-123"
            })
            
            assert len(result) == 1
            assert "🛑 Scan scan-123 has been stopped" in result[0].text
            
            mock_delete.assert_called_once_with("/scans/scan-123")

    @pytest.mark.asyncio
    async def test_get_system_health_tool(self):
        """Test the get_system_health tool."""
        with patch('mcp_server.bb_client.get') as mock_get:
            mock_get.side_effect = [
                {
                    "activeScans": 3,
                    "pendingReviews": 5, 
                    "totalRevenue": 75000,
                    "systemHealth": "operational",
                    "lastUpdate": "2025-01-15T12:00:00Z"
                },
                {
                    "total": 10,
                    "byStatus": {"needs_human": 5, "approved": 3},
                    "byType": {"XSS": 4, "SSRF": 3, "IDOR": 3}
                }
            ]
            
            result = await server.call_tool("get_system_health", {})
            
            assert len(result) == 1
            health_report = result[0].text
            
            assert "🔍 Bug Bounty Operations Health Report" in health_report
            assert "Active Scans: 3" in health_report
            assert "Total Pipeline Value: $75,000" in health_report
            assert "XSS: 4 findings" in health_report

    @pytest.mark.asyncio
    async def test_analyze_finding_tool(self):
        """Test the analyze_finding tool."""
        with patch('mcp_server.bb_client.get') as mock_get:
            mock_get.side_effect = [
                [{"id": "f1", "type": "XSS", "severity": 7.5, "status": "needs_human", "programId": "p1", "payoutEst": 5000}],  # findings
                [{"id": "p1", "name": "Test Program", "platform": "H1", "payoutMax": 10000, "triageDays": 7, "autoOK": True, "rps": 1.0}]  # programs
            ]
            
            result = await server.call_tool("analyze_finding", {
                "finding_id": "f1"
            })
            
            assert len(result) == 1
            analysis = result[0].text
            
            assert "🔍 Vulnerability Finding Analysis" in analysis
            assert "Finding ID: f1" in analysis
            assert "Type: XSS" in analysis
            assert "🟠 High" in analysis  # severity 7.5
            assert "Estimated Payout: $5,000" in analysis

    @pytest.mark.asyncio
    async def test_analyze_finding_not_found(self):
        """Test analyzing non-existent finding."""
        with patch('mcp_server.bb_client.get') as mock_get:
            mock_get.return_value = []  # No findings
            
            result = await server.call_tool("analyze_finding", {
                "finding_id": "invalid"
            })
            
            assert len(result) == 1
            assert "❌ Finding invalid not found" in result[0].text

    @pytest.mark.asyncio
    async def test_unknown_tool(self):
        """Test calling an unknown tool."""
        result = await server.call_tool("unknown_tool", {})
        
        assert len(result) == 1
        assert "❌ Unknown tool: unknown_tool" in result[0].text