# Bug Bounty Operations Center

Automated intelligence collection system with safe automation boundaries and human oversight. Processes Certificate Transparency logs at scale while respecting API rate limits and maintaining zero target interaction.

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

### Safe Automated Intelligence Pipeline
- **Certificate Transparency monitoring** - High-frequency automated processing
- **Respectful API integration** - Rate-limited queries to Shodan, VirusTotal
- **AI-powered pattern analysis** - Automated correlation of collected data
- **Human-AI collaboration** - Manual research with AI assistance
- **Zero target interaction** - All data from public sources and databases

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web UI        │    │   Claude Code    │    │ Safe Automation │
│   (Human Loop)  │◄──►│   (MCP Client)   │◄──►│   CT Logs +     │
└─────────────────┘    └──────────────────┘    │   Rate Limited  │
         │                       │              │   APIs          │
         ▼                       ▼              └─────────────────┘
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                              │
│  • Real-time updates (WebSocket)                               │
│  • MCP server endpoints                                        │
│  • AI pattern analysis engine                                 │
│  • Respectful API management                                  │
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

- `start_intelligence_collection` - Launch safe automated data collection
- `approve_finding` - Approve finding for platform submission  
- `get_research_leads` - Get AI-generated prioritized research leads
- `get_system_health` - Comprehensive system metrics and API usage
- `analyze_finding` - AI-powered finding analysis with confidence scoring

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
# Check system health and API usage
What's the current status of the intelligence collection system?

# Start safe automated collection
Start intelligence collection for the GitHub bug bounty program

# Get research leads for manual investigation
What are the top priority research leads requiring human investigation?

# Analyze findings with AI assistance
Analyze finding f2 and tell me the confidence score and manual verification steps needed
```

## 📊 Success Metrics

**Target KPIs:**
- **Discovery Rate**: 20-50 vulnerabilities per major organization
- **Confidence Accuracy**: 80%+ of high-confidence findings accepted
- **Coverage**: 95%+ subdomain discovery rate via passive reconnaissance
- **Time to Discovery**: <48 hours from target addition to vulnerability identification
- **False Positive Rate**: <10% for findings marked as "ready for submission"

## 🔒 Safety & Ethics

- **Zero target interaction** - No direct contact with target systems
- **Safe automation boundaries** - CT logs unlimited, APIs rate-limited
- **Respectful API usage** - Honor all terms of service and rate limits
- **Manual research initiation** - GitHub/Google searches human-initiated only
- **Human approval gates** - AI assists, humans decide
- **Complete legal compliance** - No scanning behavior that triggers monitoring

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
│   ├── collectors/      # Passive data collectors
│   ├── analyzers/       # Vulnerability detection
│   └── mcp_server.py    # MCP server for Claude Code
├── ui/                  # React frontend
│   ├── src/             # Source code
│   └── dist/            # Built assets
├── docs/                # Documentation
│   ├── ARCHITECTURE.md  # System architecture
│   ├── PASSIVE_SCANNING_DESIGN.md # Passive reconnaissance design
│   └── IMPLEMENTATION_PLAN.md     # Development roadmap
├── flow/                # Claude Flow configuration
│   ├── claude_flow.yaml # Agent orchestration
│   └── prompts/         # Agent prompts
├── ops/                 # Operations & deployment
│   └── docker-compose.yml
└── profiles/            # Tool configurations
```

## 🚨 Important Notes

1. **Human oversight required** - Never run fully autonomous
2. **Passive reconnaissance only** - No direct target system interaction
3. **Evidence preservation** - All findings include confidence scores and proof
4. **Platform compliance** - Follows ToS for all bounty programs and data sources
5. **Legal safety** - Uses only publicly available information

## 📖 Documentation

- **[Architecture Overview](docs/ARCHITECTURE.md)** - Detailed system design and component interactions
- **[Safe Automation Design](docs/SAFE_AUTOMATION_DESIGN.md)** - Legal automation boundaries and implementation
- **[Implementation Plan](docs/IMPLEMENTATION_PLAN.md)** - Development roadmap and technical specifications

## 🤝 Contributing

This is a defensive security tool designed for ethical bug bounty hunting. Contributions should maintain focus on:
- Responsible vulnerability disclosure
- Improved human oversight capabilities  
- Enhanced automation safety measures
- Better integration with legitimate bounty platforms