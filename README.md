# Bug Bounty Operations Center

Automated bug bounty hunting system with human-in-the-loop oversight and Claude Code integration.

## 🚀 Quick Start

```bash
# 1. Setup dependencies
make setup

# 2. Build UI (React + Material-UI)
make build-ui

# 3. Start full stack
make dev
```

**Access Points:**
- **Web UI**: http://localhost:4173 (Human oversight dashboard)
- **API**: http://localhost:8080 (Backend services)  
- **API Docs**: http://localhost:8080/docs (OpenAPI/Swagger)

## 🎯 Key Features

### Web UI Dashboard
- **Real-time monitoring** of active scans and findings
- **Human approval workflow** for vulnerability submissions
- **Evidence viewer** with screenshots and HTTP requests
- **Analytics dashboard** with revenue tracking and ROI analysis
- **Manual controls** to start/stop scans and adjust parameters

### Claude Code Integration (MCP)
- **Direct system access** via MCP server
- **Automated analysis** of findings and system health
- **Command execution** for scans, approvals, and system management
- **Real-time querying** of system state and analytics

### Automation Pipeline
- **6-agent Claude Flow** orchestration (recon → analysis → exploitation → reporting)
- **Platform integration** with HackerOne, Bugcrowd, Intigriti
- **Scope validation** and rate limiting for ethical operation
- **Safe PoC generation** without system damage

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web UI        │    │   Claude Code    │    │  Claude Flow    │
│   (Human Loop)  │◄──►│   (MCP Client)   │◄──►│   (Agents)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                              │
│  • Real-time updates (WebSocket)                               │
│  • MCP server endpoints                                        │
│  • Platform integrations                                       │
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│              Infrastructure                                     │
│  PostgreSQL │ Redis │ MinIO │ Docker Compose                   │
└─────────────────────────────────────────────────────────────────┘
```

## 🔧 MCP Server Setup

### For Claude Code Integration

1. **Install MCP dependencies:**
   ```bash
   pip install mcp httpx
   ```

2. **Add to Claude Code MCP config:**
   ```json
   {
     "mcpServers": {
       "bugbounty-ops": {
         "command": "python",
         "args": ["engine/mcp_server.py"],
         "cwd": "/path/to/bug-bounty-hunter",
         "env": {
           "PYTHONPATH": "."
         }
       }
     }
   }
   ```

3. **Start the system:**
   ```bash
   make dev  # Start backend services
   ```

### Available MCP Tools

- `start_scan` - Launch vulnerability scan for specific program
- `approve_finding` - Approve finding for platform submission  
- `stop_scan` - Halt running scan
- `get_system_health` - Comprehensive system metrics
- `analyze_finding` - Detailed finding analysis

### Available MCP Resources

- `bugbounty://status` - Real-time system status
- `bugbounty://programs` - Available bug bounty programs
- `bugbounty://findings` - All vulnerability findings
- `bugbounty://scans` - Active scan statuses
- `bugbounty://analytics` - Revenue and performance data

## 🎮 Usage Examples

### Via Web UI
1. Navigate to http://localhost:4173
2. Click "Scan" on any program to start hunting
3. Review findings in "Findings Requiring Review" table
4. Click approve button after manual verification
5. Monitor progress in real-time dashboard

### Via Claude Code (MCP)
```
# Check system health
What's the current status of the bug bounty system?

# Start a scan
Start a scan for the GitHub bug bounty program with high priority

# Analyze findings
Analyze finding f2 and tell me if it's worth submitting

# Get system insights
Show me revenue trends and most profitable vulnerability types
```

## 📊 Success Metrics

**Target KPIs:**
- **Monthly Revenue**: $25,000+ from automated discoveries
- **Submission Rate**: 100+ vulnerability reports per month  
- **Success Rate**: 15%+ acceptance rate on submissions
- **Time to Discovery**: <24 hours from target ID to confirmed vulnerability

## 🔒 Safety & Ethics

- **Scope validation** before any testing
- **Rate limiting** to prevent service disruption
- **No destructive testing** - safe PoC generation only
- **Responsible disclosure** with proper timelines
- **Human approval gates** for all submissions

## 🛠️ Development Commands

```bash
make help          # Show all available commands
make setup         # Install dependencies
make build-ui      # Build React frontend
make dev           # Full stack development
make api           # API server only
make workers       # Background workers only
make stop          # Stop all services
make clean         # Clean build artifacts
make bundle        # Create Claude Flow deployment package
make mcp-test      # Test MCP server
```

## 📁 Project Structure

```
bug-bounty-hunter/
├── engine/               # Backend services
│   ├── api/             # FastAPI application
│   ├── scanner-farm/    # Vulnerability scanners
│   ├── safe-poc/        # PoC generation
│   └── mcp_server.py    # MCP server for Claude Code
├── ui/                  # React frontend
│   ├── src/             # Source code
│   └── dist/            # Built assets
├── flow/                # Claude Flow configuration
│   ├── claude_flow.yaml # Agent orchestration
│   └── prompts/         # Agent prompts
├── ops/                 # Operations & deployment
│   └── docker-compose.yml
└── profiles/            # Tool configurations
```

## 🚨 Important Notes

1. **Human oversight required** - Never run fully autonomous
2. **Rate limits enforced** - Respects program guidelines
3. **Evidence preservation** - All findings include proof
4. **Platform compliance** - Follows ToS for all bounty programs
5. **Revenue tracking** - Built-in ROI analysis and reporting

## 🤝 Contributing

This is a defensive security tool designed for ethical bug bounty hunting. Contributions should maintain focus on:
- Responsible vulnerability disclosure
- Improved human oversight capabilities  
- Enhanced automation safety measures
- Better integration with legitimate bounty platforms