from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="BugBountyOps API")

PROGRAMS = [
    {"id":"h1-google","name":"Google VRP","platform":"H1","payoutMax":1000000,"rps":0.5,"autoOK":True,"triageDays":14,"assetCount":2800,"tags":["web","mobile","cloud"]},
    {"id":"apple-vrp","name":"Apple Security Bounty","platform":"Direct","payoutMax":1000000,"rps":0.2,"autoOK":False,"triageDays":30,"assetCount":120,"tags":["mobile","kernel"]},
    {"id":"msrc","name":"Microsoft (MSRC)","platform":"Direct","payoutMax":40000,"rps":0.5,"autoOK":True,"triageDays":10,"assetCount":900,"tags":["cloud","desktop","ai"]},
    {"id":"github","name":"GitHub","platform":"H1","payoutMax":30000,"rps":1.0,"autoOK":True,"triageDays":7,"assetCount":700,"tags":["dev","api","actions"]},
]
FINDINGS = [
    {"id":"f1","programId":"github","type":"IDOR","severity":7.5,"status":"ready_to_submit","payoutEst":8000},
    {"id":"f2","programId":"h1-google","type":"SSRF","severity":8.8,"status":"needs_human","payoutEst":25000},
    {"id":"f3","programId":"msrc","type":"AuthZ bypass","severity":9.1,"status":"queued","payoutEst":15000},
]

@app.get("/programs")
def programs(): return PROGRAMS

@app.post("/queue")
def queue(program_id: str, priority: str = "fast_pay"):
    return {"queued": True, "program_id": program_id, "priority": priority}

@app.get("/findings")
def findings(status: str | None = None):
    return [f for f in FINDINGS if not status or f["status"]==status]
