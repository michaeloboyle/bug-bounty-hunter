#!/usr/bin/env python3
"""
MCP Server for Bug Bounty Operations
Provides Claude Code with direct access to bug bounty system
"""
import asyncio
import json
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

import httpx
from mcp import McpServer, Resource, Tool
from mcp.types import TextContent

# MCP Server instance
server = McpServer("bugbounty-ops")

# API base URL
API_BASE = "http://localhost:8080"

class BugBountyOpsClient:
    """Client for interacting with Bug Bounty Ops API"""
    
    def __init__(self, base_url: str = API_BASE):
        self.base_url = base_url
        
    async def get(self, endpoint: str) -> Dict[str, Any]:
        """Make GET request to API"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}{endpoint}")
            response.raise_for_status()
            return response.json()
    
    async def post(self, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make POST request to API"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}{endpoint}", 
                json=data if data else {}
            )
            response.raise_for_status()
            return response.json()
    
    async def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make DELETE request to API"""
        async with httpx.AsyncClient() as client:
            response = await client.delete(f"{self.base_url}{endpoint}")
            response.raise_for_status()
            return response.json()

# Initialize client
bb_client = BugBountyOpsClient()

# Resources
@server.list_resources()
async def list_resources() -> List[Resource]:
    """List available resources"""
    return [
        Resource(
            uri="bugbounty://status",
            name="System Status",
            description="Current system status including active scans and findings",
            mimeType="application/json"
        ),
        Resource(
            uri="bugbounty://programs",
            name="Bug Bounty Programs",
            description="All available bug bounty programs",
            mimeType="application/json"
        ),
        Resource(
            uri="bugbounty://findings",
            name="Vulnerability Findings",
            description="All discovered vulnerability findings",
            mimeType="application/json"
        ),
        Resource(
            uri="bugbounty://scans",
            name="Active Scans",
            description="Currently running vulnerability scans",
            mimeType="application/json"
        ),
        Resource(
            uri="bugbounty://analytics",
            name="Analytics Dashboard",
            description="Revenue, vulnerability type, and performance analytics",
            mimeType="application/json"
        )
    ]

@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read a specific resource"""
    try:
        if uri == "bugbounty://status":
            status = await bb_client.get("/mcp/status")
            return json.dumps(status, indent=2)
        
        elif uri == "bugbounty://programs":
            programs = await bb_client.get("/programs")
            return json.dumps(programs, indent=2)
        
        elif uri == "bugbounty://findings":
            findings = await bb_client.get("/findings")
            findings_summary = await bb_client.get("/mcp/findings/summary")
            return json.dumps({
                "summary": findings_summary,
                "findings": findings
            }, indent=2)
        
        elif uri == "bugbounty://scans":
            scans = await bb_client.get("/scans")
            return json.dumps(scans, indent=2)
        
        elif uri == "bugbounty://analytics":
            revenue = await bb_client.get("/analytics/revenue")
            vulns = await bb_client.get("/analytics/vulnerabilities")
            return json.dumps({
                "revenue_trend": revenue,
                "vulnerability_types": vulns
            }, indent=2)
        
        else:
            raise ValueError(f"Unknown resource: {uri}")
            
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

# Tools
@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools"""
    return [
        Tool(
            name="start_scan",
            description="Start a vulnerability scan for a specific program",
            inputSchema={
                "type": "object",
                "properties": {
                    "program_id": {
                        "type": "string",
                        "description": "ID of the bug bounty program to scan"
                    },
                    "priority": {
                        "type": "string",
                        "description": "Scan priority (high_ceiling, fast_pay, mobile, web3)",
                        "default": "fast_pay"
                    }
                },
                "required": ["program_id"]
            }
        ),
        Tool(
            name="approve_finding",
            description="Approve a vulnerability finding for submission",
            inputSchema={
                "type": "object",
                "properties": {
                    "finding_id": {
                        "type": "string",
                        "description": "ID of the finding to approve"
                    }
                },
                "required": ["finding_id"]
            }
        ),
        Tool(
            name="stop_scan",
            description="Stop a running vulnerability scan",
            inputSchema={
                "type": "object",
                "properties": {
                    "scan_id": {
                        "type": "string",
                        "description": "ID of the scan to stop"
                    }
                },
                "required": ["scan_id"]
            }
        ),
        Tool(
            name="get_system_health",
            description="Get comprehensive system health and performance metrics",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ),
        Tool(
            name="analyze_finding",
            description="Get detailed analysis of a specific finding",
            inputSchema={
                "type": "object",
                "properties": {
                    "finding_id": {
                        "type": "string",
                        "description": "ID of the finding to analyze"
                    }
                },
                "required": ["finding_id"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls"""
    try:
        if name == "start_scan":
            program_id = arguments["program_id"]
            priority = arguments.get("priority", "fast_pay")
            
            result = await bb_client.post("/queue", {
                "program_id": program_id,
                "priority": priority
            })
            
            return [TextContent(
                type="text",
                text=f"✅ Scan started for program {program_id}\n"
                     f"Scan ID: {result.get('scan_id', 'N/A')}\n"
                     f"Priority: {priority}\n"
                     f"Status: Queued and will begin processing shortly"
            )]
        
        elif name == "approve_finding":
            finding_id = arguments["finding_id"]
            
            result = await bb_client.post(f"/findings/{finding_id}/approve")
            
            return [TextContent(
                type="text",
                text=f"✅ Finding {finding_id} has been approved for submission\n"
                     f"Status: The finding will be prepared for platform submission\n"
                     f"Next: Automated submission to appropriate bug bounty platform"
            )]
        
        elif name == "stop_scan":
            scan_id = arguments["scan_id"]
            
            result = await bb_client.delete(f"/scans/{scan_id}")
            
            return [TextContent(
                type="text",
                text=f"🛑 Scan {scan_id} has been stopped\n"
                     f"Status: Scan terminated and resources freed\n"
                     f"Any partial findings have been preserved"
            )]
        
        elif name == "get_system_health":
            status = await bb_client.get("/mcp/status")
            findings_summary = await bb_client.get("/mcp/findings/summary")
            
            health_report = f"""🔍 Bug Bounty Operations Health Report

📊 ACTIVE OPERATIONS
• Active Scans: {status['activeScans']}
• Pending Reviews: {status['pendingReviews']}
• System Health: {status['systemHealth'].upper()}

💰 FINANCIAL METRICS
• Total Pipeline Value: ${status['totalRevenue']:,}
• Total Findings: {findings_summary['total']}
• Estimated Monthly Revenue: ${status['totalRevenue'] // 12:,}

📈 FINDINGS BREAKDOWN
• Needs Human Review: {findings_summary['byStatus'].get('needs_human', 0)}
• Ready to Submit: {findings_summary['byStatus'].get('ready_to_submit', 0)}
• Approved: {findings_summary['byStatus'].get('approved', 0)}

🎯 VULNERABILITY TYPES
"""
            for vuln_type, count in findings_summary['byType'].items():
                health_report += f"• {vuln_type}: {count} findings\n"
            
            health_report += f"\n⏰ Last Updated: {status['lastUpdate']}"
            
            return [TextContent(type="text", text=health_report)]
        
        elif name == "analyze_finding":
            finding_id = arguments["finding_id"]
            
            # Get all findings and find the specific one
            findings = await bb_client.get("/findings")
            finding = next((f for f in findings if f["id"] == finding_id), None)
            
            if not finding:
                return [TextContent(
                    type="text",
                    text=f"❌ Finding {finding_id} not found"
                )]
            
            # Get program details
            programs = await bb_client.get("/programs")
            program = next((p for p in programs if p["id"] == finding["programId"]), None)
            
            severity_labels = {
                (9.0, 10.0): "🔴 Critical",
                (7.0, 9.0): "🟠 High", 
                (4.0, 7.0): "🟡 Medium",
                (0.1, 4.0): "🟢 Low",
                (0.0, 0.1): "ℹ️ Info"
            }
            
            severity_label = "Unknown"
            for (min_val, max_val), label in severity_labels.items():
                if min_val <= finding["severity"] < max_val:
                    severity_label = label
                    break
            
            analysis = f"""🔍 Vulnerability Finding Analysis

📋 BASIC INFO
• Finding ID: {finding_id}
• Type: {finding['type']}
• Severity: {finding['severity']} ({severity_label})
• Status: {finding['status'].replace('_', ' ').title()}
• Program: {program['name'] if program else 'Unknown'}

💰 FINANCIAL IMPACT
• Estimated Payout: ${finding['payoutEst']:,}
• Program Max Payout: ${program['payoutMax']:,} if program else 'Unknown'}
• Platform: {program['platform'] if program else 'Unknown'}

📊 PROGRAM DETAILS
• Triage Timeline: {program['triageDays']} days if program else 'Unknown'}
• Auto-approval: {'Yes' if program and program['autoOK'] else 'No'}
• Rate Limit: {program['rps']} req/sec if program else 'Unknown'}

🔍 EVIDENCE
"""
            if finding.get('evidence'):
                for i, evidence in enumerate(finding['evidence'], 1):
                    analysis += f"• {i}. {evidence}\n"
            else:
                analysis += "• No evidence recorded\n"
            
            analysis += f"""
📅 TIMELINE
• Discovered: {finding.get('timestamp', 'Unknown')}
• Last Updated: {finding.get('updatedAt', 'Not updated')}

🎯 NEXT ACTIONS
"""
            if finding['status'] == 'needs_human':
                analysis += "• Human review required before submission\n"
                analysis += "• Use 'approve_finding' tool if ready to submit\n"
            elif finding['status'] == 'approved':
                analysis += "• Approved for submission to platform\n"
                analysis += "• Will be automatically submitted\n"
            elif finding['status'] == 'queued':
                analysis += "• In processing queue\n"
                analysis += "• Awaiting automated analysis\n"
            
            return [TextContent(type="text", text=analysis)]
        
        else:
            return [TextContent(
                type="text",
                text=f"❌ Unknown tool: {name}"
            )]
            
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"❌ Error executing {name}: {str(e)}"
        )]

async def main():
    """Main MCP server entry point"""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())