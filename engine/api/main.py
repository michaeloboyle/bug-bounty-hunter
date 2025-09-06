import asyncio
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional

import socketio
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Socket.IO for real-time updates
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=[])
socket_app = socketio.ASGIApp(sio)

app = FastAPI(title="BugBountyOps API")


# Data Models
class ScanRequest(BaseModel):
    program_id: str
    priority: str = "fast_pay"


class FindingApproval(BaseModel):
    finding_id: str
    approved: bool
    notes: Optional[str] = None

# In-memory data (replace with database in production)
PROGRAMS = [
    {
        "id": "h1-google",
        "name": "Google VRP",
        "platform": "H1",
        "payoutMax": 1000000,
        "rps": 0.5,
        "autoOK": True,
        "triageDays": 14,
        "assetCount": 2800,
        "tags": ["web", "mobile", "cloud"],
    },
    {
        "id": "apple-vrp",
        "name": "Apple Security Bounty",
        "platform": "Direct",
        "payoutMax": 1000000,
        "rps": 0.2,
        "autoOK": False,
        "triageDays": 30,
        "assetCount": 120,
        "tags": ["mobile", "kernel"],
    },
    {
        "id": "msrc",
        "name": "Microsoft (MSRC)",
        "platform": "Direct",
        "payoutMax": 40000,
        "rps": 0.5,
        "autoOK": True,
        "triageDays": 10,
        "assetCount": 900,
        "tags": ["cloud", "desktop", "ai"],
    },
    {
        "id": "github",
        "name": "GitHub",
        "platform": "H1",
        "payoutMax": 30000,
        "rps": 1.0,
        "autoOK": True,
        "triageDays": 7,
        "assetCount": 700,
        "tags": ["dev", "api", "actions"],
    },
]

FINDINGS = [
    {"id":"f1","programId":"github","type":"IDOR","severity":7.5,"status":"ready_to_submit","payoutEst":8000,"timestamp":"2025-01-15T10:30:00Z","evidence":["Screenshot of unauthorized access","HTTP request showing missing authz check"]},
    {"id":"f2","programId":"h1-google","type":"SSRF","severity":8.8,"status":"needs_human","payoutEst":25000,"timestamp":"2025-01-15T14:22:00Z","evidence":["Internal service response","Network diagram showing impact"]},
    {"id":"f3","programId":"msrc","type":"AuthZ bypass","severity":9.1,"status":"queued","payoutEst":15000,"timestamp":"2025-01-15T09:15:00Z","evidence":["Admin panel access proof","User privilege escalation"]},
]

SCAN_STATUSES = {}

# Activity tracking - GitHub Actions style
ACTIVITIES = []
ACTIVITY_RUNS = {}
ACTIVITY_LOGS = {}
ARTIFACTS = {}

# API Routes
@app.get("/programs")
async def get_programs():
    """Get all available bug bounty programs"""
    return PROGRAMS

@app.post("/queue")
async def queue_scan(request: ScanRequest):
    """Queue a new scan for a program"""
    program = next((p for p in PROGRAMS if p["id"] == request.program_id), None)
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    
    scan_id = str(uuid.uuid4())
    scan_status = {
        "id": scan_id,
        "programId": request.program_id,
        "status": "queued",
        "progress": 0,
        "assetsFound": 0,
        "vulnerabilitiesFound": 0,
        "startTime": datetime.now().isoformat()
    }
    
    SCAN_STATUSES[scan_id] = scan_status
    
    # Emit real-time update
    await sio.emit('scan_update', scan_status)
    
    # Start background scan simulation
    asyncio.create_task(simulate_scan(scan_id))
    
    return {"queued": True, "scan_id": scan_id, "program_id": request.program_id, "priority": request.priority}

@app.get("/findings")
async def get_findings(status: Optional[str] = None):
    """Get findings, optionally filtered by status"""
    filtered = [f for f in FINDINGS if not status or f["status"] == status]
    return filtered

@app.post("/findings/{finding_id}/approve")
async def approve_finding(finding_id: str):
    """Approve a finding for submission"""
    finding = next((f for f in FINDINGS if f["id"] == finding_id), None)
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    
    finding["status"] = "approved"
    finding["approvedAt"] = datetime.now().isoformat()
    
    # Emit real-time update
    await sio.emit('finding_approved', finding)
    
    return {"approved": True, "finding_id": finding_id}

@app.get("/scans")
async def get_scan_statuses():
    """Get all scan statuses"""
    return list(SCAN_STATUSES.values())

@app.get("/scans/{scan_id}")
async def get_scan_status(scan_id: str):
    """Get specific scan status"""
    if scan_id not in SCAN_STATUSES:
        raise HTTPException(status_code=404, detail="Scan not found")
    return SCAN_STATUSES[scan_id]

@app.delete("/scans/{scan_id}")
async def stop_scan(scan_id: str):
    """Stop a running scan"""
    if scan_id not in SCAN_STATUSES:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    SCAN_STATUSES[scan_id]["status"] = "stopped"
    await sio.emit('scan_update', SCAN_STATUSES[scan_id])
    
    return {"stopped": True, "scan_id": scan_id}

@app.get("/analytics/revenue")
async def get_revenue_analytics():
    """Get revenue analytics data"""
    return [
        {"month": "Jan", "revenue": 15000, "submissions": 45},
        {"month": "Feb", "revenue": 22000, "submissions": 67},
        {"month": "Mar", "revenue": 31000, "submissions": 89},
        {"month": "Apr", "revenue": 28000, "submissions": 76},
        {"month": "May", "revenue": 35000, "submissions": 95}
    ]

@app.get("/analytics/vulnerabilities")
async def get_vulnerability_analytics():
    """Get vulnerability type analytics"""
    return [
        {"name": "SSRF", "value": 12, "payout": 45000},
        {"name": "IDOR", "value": 8, "payout": 23000},
        {"name": "XSS", "value": 15, "payout": 15000},
        {"name": "AuthZ", "value": 6, "payout": 32000},
        {"name": "Other", "value": 9, "payout": 8000}
    ]

# MCP Server Endpoints for Claude Code Integration
@app.get("/mcp/status")
async def mcp_status():
    """MCP endpoint for system status"""
    active_scans = len([s for s in SCAN_STATUSES.values() if s["status"] not in ["completed", "stopped"]])
    pending_reviews = len([f for f in FINDINGS if f["status"] == "needs_human"])
    total_revenue = sum(f["payoutEst"] for f in FINDINGS if f["status"] in ["approved", "submitted"])
    
    return {
        "activeScans": active_scans,
        "pendingReviews": pending_reviews,
        "totalRevenue": total_revenue,
        "systemHealth": "operational",
        "lastUpdate": datetime.now().isoformat()
    }

@app.get("/mcp/findings/summary")
async def mcp_findings_summary():
    """MCP endpoint for findings summary"""
    return {
        "total": len(FINDINGS),
        "byStatus": {
            status: len([f for f in FINDINGS if f["status"] == status])
            for status in ["queued", "needs_human", "approved", "submitted", "paid"]
        },
        "byType": {
            vuln_type: len([f for f in FINDINGS if f["type"] == vuln_type])
            for vuln_type in set(f["type"] for f in FINDINGS)
        },
        "totalValue": sum(f["payoutEst"] for f in FINDINGS)
    }

@app.post("/mcp/scan/start")
async def mcp_start_scan(program_id: str, priority: str = "fast_pay"):
    """MCP endpoint to start a scan"""
    return await queue_scan(ScanRequest(program_id=program_id, priority=priority))

# Socket.IO Events
@sio.event
async def connect(sid, environ):
    logger.info(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    logger.info(f"Client disconnected: {sid}")

# Background scan simulation with activity tracking
async def simulate_scan(scan_id: str):
    """Simulate a vulnerability scan with detailed activity tracking"""
    scan = SCAN_STATUSES[scan_id]
    program = next((p for p in PROGRAMS if p["id"] == scan["programId"]), None)
    program_name = program["name"] if program else scan["programId"]
    
    # Create activity for this scan
    activity_id = create_activity(
        "scan",
        f"Vulnerability Scan: {program_name}",
        scan["programId"],
        "automated"
    )
    
    scan["activityId"] = activity_id
    update_activity_status(activity_id, "in_progress")
    log_activity(activity_id, "info", f"Starting vulnerability scan for {program_name}")
    
    stages = [
        ("scanning", "Asset Discovery", 20, "recon"),
        ("analyzing", "Vulnerability Analysis", 40, "analysis"), 
        ("exploiting", "Exploit Testing", 70, "exploitation"),
        ("reporting", "Report Generation", 90, "reporting"),
        ("completed", "Scan Complete", 100, "completion")
    ]
    
    try:
        for status, description, progress, job_name in stages:
            if scan["status"] == "stopped":
                update_activity_status(activity_id, "cancelled", "cancelled")
                log_activity(activity_id, "warning", "Scan cancelled by user")
                break
                
            # Create run for this stage
            run_id = create_activity_run(activity_id, job_name, description)
            
            scan["status"] = status
            scan["progress"] = progress
            scan["assetsFound"] = min(progress // 10, 15)
            scan["vulnerabilitiesFound"] = max(0, (progress - 30) // 20)
            
            # Log stage start
            log_activity(activity_id, "info", f"Started {description}", run_id)
            
            # Simulate stage work
            await sio.emit('scan_update', scan)
            await asyncio.sleep(2)
            
            # Add detailed logs for each stage
            if job_name == "recon":
                log_activity(activity_id, "info", f"Discovering subdomains for {program_name}", run_id)
                add_artifact(activity_id, "subdomain_list.txt", 
                           f"api.{program_name.lower().replace(' ', '')}.com\nadmin.{program_name.lower().replace(' ', '')}.com\napp.{program_name.lower().replace(' ', '')}.com", 
                           "text", run_id)
                log_activity(activity_id, "success", f"Found {scan['assetsFound']} assets", run_id)
                
            elif job_name == "analysis":
                log_activity(activity_id, "info", "Running Nuclei vulnerability templates", run_id)
                log_activity(activity_id, "info", "Checking for common misconfigurations", run_id)
                if scan["vulnerabilitiesFound"] > 0:
                    log_activity(activity_id, "warning", f"Potential vulnerabilities detected: {scan['vulnerabilitiesFound']}", run_id)
                
            elif job_name == "exploitation":
                if scan["vulnerabilitiesFound"] > 0:
                    log_activity(activity_id, "info", "Generating safe proof-of-concept exploits", run_id)
                    
                    # Create a new finding
                    new_finding = {
                        "id": f"f{len(FINDINGS) + 1}",
                        "programId": scan["programId"],
                        "type": "XSS",
                        "severity": 6.5,
                        "status": "needs_human",
                        "payoutEst": 5000,
                        "timestamp": datetime.now().isoformat(),
                        "evidence": ["XSS payload execution proof", "Impact demonstration"],
                        "activityId": activity_id
                    }
                    FINDINGS.append(new_finding)
                    
                    # Add artifacts
                    add_artifact(activity_id, "xss_poc.html", 
                               "<script>alert('XSS found in search parameter')</script>", 
                               "text", run_id)
                    add_artifact(activity_id, "http_request.txt", 
                               f"GET /search?q=<script>alert(1)</script> HTTP/1.1\nHost: {program_name.lower().replace(' ', '')}.com\n", 
                               "http_request", run_id)
                    
                    log_activity(activity_id, "success", f"Generated finding: {new_finding['id']}", run_id)
                    await sio.emit('new_finding', new_finding)
                
            elif job_name == "reporting":
                log_activity(activity_id, "info", "Compiling vulnerability report", run_id)
                if scan["vulnerabilitiesFound"] > 0:
                    report_content = f"""# Vulnerability Scan Report - {program_name}

## Summary
- Assets Discovered: {scan['assetsFound']}
- Vulnerabilities Found: {scan['vulnerabilitiesFound']}
- Severity: Medium
- Estimated Payout: $5,000

## Findings
1. Cross-Site Scripting (XSS) in search functionality
   - Impact: User session hijacking
   - Affected URL: search endpoint
   - CVSS: 6.5 (Medium)
"""
                    add_artifact(activity_id, "vulnerability_report.md", report_content, "text", run_id)
                    log_activity(activity_id, "success", "Vulnerability report generated", run_id)
                else:
                    log_activity(activity_id, "info", "No vulnerabilities found - scan complete", run_id)
            
            # Update run status
            for activity in ACTIVITIES:
                if activity["id"] == activity_id:
                    runs = ACTIVITY_RUNS.get(activity_id, [])
                    for run in runs:
                        if run["id"] == run_id:
                            run["status"] = "completed"
                            run["conclusion"] = "success"
                            run["endTime"] = datetime.now().isoformat()
                            break
                    break
        
        # Complete the activity
        if scan["status"] != "stopped":
            update_activity_status(activity_id, "completed", "success")
            log_activity(activity_id, "success", f"Scan completed successfully. Found {scan['vulnerabilitiesFound']} vulnerabilities.")
        
    except Exception as e:
        update_activity_status(activity_id, "failed", "failure")
        log_activity(activity_id, "error", f"Scan failed: {str(e)}")
        scan["status"] = "failed"
    
    await sio.emit('scan_update', scan)
    await sio.emit('activity_updated', next(a for a in ACTIVITIES if a["id"] == activity_id))

# Activity tracking functions
def create_activity(activity_type: str, title: str, program_id: str = None, triggered_by: str = "system") -> str:
    """Create a new activity (like GitHub Actions workflow)"""
    activity_id = str(uuid.uuid4())
    activity = {
        "id": activity_id,
        "type": activity_type,  # "scan", "submission", "analysis", "manual"
        "title": title,
        "programId": program_id,
        "triggeredBy": triggered_by,
        "status": "queued",  # queued, in_progress, completed, failed, cancelled
        "startTime": datetime.now().isoformat(),
        "endTime": None,
        "duration": None,
        "conclusion": None,  # success, failure, cancelled, skipped
        "artifacts": [],
        "runCount": 0
    }
    ACTIVITIES.append(activity)
    ACTIVITY_RUNS[activity_id] = []
    ACTIVITY_LOGS[activity_id] = []
    return activity_id

def create_activity_run(activity_id: str, job_name: str, step_name: str = None) -> str:
    """Create a run within an activity (like GitHub Actions job)"""
    run_id = str(uuid.uuid4())
    run = {
        "id": run_id,
        "activityId": activity_id,
        "jobName": job_name,
        "stepName": step_name,
        "status": "queued",
        "startTime": datetime.now().isoformat(),
        "endTime": None,
        "duration": None,
        "conclusion": None,
        "logs": [],
        "artifacts": []
    }
    
    if activity_id not in ACTIVITY_RUNS:
        ACTIVITY_RUNS[activity_id] = []
    ACTIVITY_RUNS[activity_id].append(run)
    return run_id

def log_activity(activity_id: str, level: str, message: str, run_id: str = None):
    """Add log entry to activity (with optional run context)"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "level": level,  # info, warning, error, success
        "message": message,
        "runId": run_id
    }
    
    if activity_id not in ACTIVITY_LOGS:
        ACTIVITY_LOGS[activity_id] = []
    ACTIVITY_LOGS[activity_id].append(log_entry)

def update_activity_status(activity_id: str, status: str, conclusion: str = None):
    """Update activity status and conclusion"""
    for activity in ACTIVITIES:
        if activity["id"] == activity_id:
            activity["status"] = status
            if conclusion:
                activity["conclusion"] = conclusion
            if status in ["completed", "failed", "cancelled"]:
                activity["endTime"] = datetime.now().isoformat()
                start_time = datetime.fromisoformat(activity["startTime"])
                end_time = datetime.fromisoformat(activity["endTime"])
                activity["duration"] = int((end_time - start_time).total_seconds())
            break

def add_artifact(activity_id: str, name: str, content: str, artifact_type: str = "text", run_id: str = None):
    """Add artifact to activity (evidence, logs, reports)"""
    artifact_id = str(uuid.uuid4())
    artifact = {
        "id": artifact_id,
        "name": name,
        "type": artifact_type,  # text, image, json, http_request, screenshot
        "content": content,
        "size": len(content),
        "createdAt": datetime.now().isoformat(),
        "runId": run_id
    }
    
    ARTIFACTS[artifact_id] = artifact
    
    # Add to activity
    for activity in ACTIVITIES:
        if activity["id"] == activity_id:
            activity["artifacts"].append(artifact_id)
            break

# Activity API endpoints
@app.get("/activities")
async def get_activities(
    activity_type: Optional[str] = None,
    status: Optional[str] = None,
    program_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """Get activity history with filtering (GitHub Actions style)"""
    filtered_activities = ACTIVITIES.copy()
    
    # Apply filters
    if activity_type:
        filtered_activities = [a for a in filtered_activities if a["type"] == activity_type]
    if status:
        filtered_activities = [a for a in filtered_activities if a["status"] == status]
    if program_id:
        filtered_activities = [a for a in filtered_activities if a.get("programId") == program_id]
    
    # Sort by most recent first
    filtered_activities.sort(key=lambda x: x["startTime"], reverse=True)
    
    # Paginate
    total = len(filtered_activities)
    paginated = filtered_activities[offset:offset + limit]
    
    # Add run counts
    for activity in paginated:
        activity["runCount"] = len(ACTIVITY_RUNS.get(activity["id"], []))
    
    return {
        "activities": paginated,
        "total": total,
        "hasMore": offset + limit < total
    }

@app.get("/activities/{activity_id}")
async def get_activity_details(activity_id: str):
    """Get detailed activity information with runs and logs"""
    activity = next((a for a in ACTIVITIES if a["id"] == activity_id), None)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Get runs for this activity
    runs = ACTIVITY_RUNS.get(activity_id, [])
    
    # Get logs for this activity
    logs = ACTIVITY_LOGS.get(activity_id, [])
    
    # Get artifacts
    artifacts = [ARTIFACTS[aid] for aid in activity.get("artifacts", []) if aid in ARTIFACTS]
    
    return {
        **activity,
        "runs": runs,
        "logs": logs,
        "artifacts": artifacts
    }

@app.get("/activities/{activity_id}/logs")
async def get_activity_logs(activity_id: str, run_id: Optional[str] = None):
    """Get logs for specific activity (optionally filtered by run)"""
    if activity_id not in ACTIVITY_LOGS:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    logs = ACTIVITY_LOGS[activity_id]
    
    if run_id:
        logs = [log for log in logs if log.get("runId") == run_id]
    
    return {"logs": logs}

@app.get("/activities/{activity_id}/artifacts")
async def get_activity_artifacts(activity_id: str):
    """Get all artifacts for an activity"""
    activity = next((a for a in ACTIVITIES if a["id"] == activity_id), None)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    artifacts = [ARTIFACTS[aid] for aid in activity.get("artifacts", []) if aid in ARTIFACTS]
    return {"artifacts": artifacts}

@app.get("/artifacts/{artifact_id}")
async def get_artifact(artifact_id: str):
    """Get specific artifact content"""
    if artifact_id not in ARTIFACTS:
        raise HTTPException(status_code=404, detail="Artifact not found")
    
    return ARTIFACTS[artifact_id]

@app.delete("/activities/{activity_id}")
async def cancel_activity(activity_id: str):
    """Cancel a running activity"""
    activity = next((a for a in ACTIVITIES if a["id"] == activity_id), None)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    if activity["status"] not in ["queued", "in_progress"]:
        raise HTTPException(status_code=400, detail="Activity cannot be cancelled")
    
    update_activity_status(activity_id, "cancelled", "cancelled")
    log_activity(activity_id, "info", "Activity cancelled by user")
    
    await sio.emit('activity_updated', activity)
    
    return {"cancelled": True, "activity_id": activity_id}

# Mount Socket.IO
app.mount("/socket.io", socket_app)
