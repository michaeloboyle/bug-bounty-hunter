# Bug Bounty Operations - System Architecture

This document provides visual diagrams of the system architecture, process flows, and data relationships using Mermaid.

## 1. System Architecture Overview

```mermaid
graph TB
    subgraph "User Interfaces"
        WebUI[Web UI Dashboard<br/>React + Material-UI]
        ClaudeCode[Claude Code<br/>MCP Client]
    end
    
    subgraph "API Gateway"
        FastAPI[FastAPI Backend<br/>Python + Socket.IO]
        MCP[MCP Server<br/>Tools & Resources]
    end
    
    subgraph "Core Services"
        ActivityTracker[Activity Tracker<br/>GitHub Actions Style]
        ScanOrchestrator[Scan Orchestrator<br/>Task Management]
        FindingManager[Finding Manager<br/>Vulnerability Tracking]
        EvidenceStore[Evidence Store<br/>Artifact Management]
    end
    
    subgraph "External Systems"
        ClaudeFlow[Claude Flow<br/>6-Agent Pipeline]
        Platforms[Bug Bounty Platforms<br/>HackerOne, Bugcrowd]
        Tools[Security Tools<br/>Nuclei, Burp Suite]
    end
    
    subgraph "Infrastructure"
        PostgreSQL[(PostgreSQL<br/>Primary Database)]
        Redis[(Redis<br/>Task Queue)]
        MinIO[(MinIO<br/>Artifact Storage)]
    end
    
    WebUI --> FastAPI
    ClaudeCode --> MCP
    MCP --> FastAPI
    
    FastAPI --> ActivityTracker
    FastAPI -.-> ScanOrchestrator
    FastAPI -.-> FindingManager
    FastAPI -.-> EvidenceStore
    
    ScanOrchestrator -.-> ClaudeFlow
    FindingManager -.-> Platforms
    ScanOrchestrator -.-> Tools
    
    ActivityTracker -.-> PostgreSQL
    FindingManager -.-> PostgreSQL
    ScanOrchestrator -.-> Redis
    EvidenceStore -.-> MinIO
    
    style WebUI fill:#e1f5fe
    style ClaudeCode fill:#e8f5e8
    style FastAPI fill:#fff3e0
    style ActivityTracker fill:#fff3e0
    style ClaudeFlow fill:#f3e5f5,stroke-dasharray: 5 5
    style ScanOrchestrator fill:#f3e5f5,stroke-dasharray: 5 5
    style FindingManager fill:#f3e5f5,stroke-dasharray: 5 5
    style EvidenceStore fill:#f3e5f5,stroke-dasharray: 5 5
    style Platforms fill:#f3e5f5,stroke-dasharray: 5 5
    style Tools fill:#f3e5f5,stroke-dasharray: 5 5
    style PostgreSQL fill:#ffebee,stroke-dasharray: 5 5
    style Redis fill:#fff8e1,stroke-dasharray: 5 5
    style MinIO fill:#e0f2f1,stroke-dasharray: 5 5
```

## 2. Bug Bounty Process Flow

```mermaid
flowchart TD
    Start([User Initiates Scan]) --> ProgramSelect[Select Bug Bounty Program]
    ProgramSelect --> ValidateScope{Validate Scope & Permissions}
    
    ValidateScope -->|✅ Approved| CreateActivity[Create Activity Record]
    ValidateScope -->|❌ Denied| Reject[Reject - Out of Scope]
    
    CreateActivity --> InitFlow[Initialize Claude Flow Pipeline]
    
    subgraph "Claude Flow 6-Agent Pipeline"
        Coordination[🎯 Coordination Agent<br/>Scope validation, task planning]
        Recon[🔍 Reconnaissance Agent<br/>Asset discovery, enumeration]
        Analysis[🧠 Analysis Agent<br/>Vulnerability detection]
        ScannerFarm[⚙️ Scanner Farm Agent<br/>Automated testing tools]
        Exploitation[💥 Exploitation Agent<br/>Safe PoC generation]
        Reporting[📄 Reporting Agent<br/>Documentation & CVSS scoring]
    end
    
    InitFlow -.-> Coordination
    Coordination -.-> Recon
    Recon -.-> Analysis
    Analysis -.-> ScannerFarm
    ScannerFarm -.-> Exploitation
    Exploitation --> HumanGate{Human Review Required}
    
    HumanGate -->|✅ Approved| Reporting
    HumanGate -->|❌ Rejected| Archive[Archive Finding]
    HumanGate -->|🔄 Needs Changes| Exploitation
    
    Reporting -.-> AutoSubmit{Auto-Submit Enabled?}
    AutoSubmit -.->|Yes| SubmitPlatform[Submit to Platform]
    AutoSubmit -->|No| QueueReview[Queue for Manual Review]
    
    SubmitPlatform -.-> TrackPayout[Track Payout Status]
    QueueReview --> ManualSubmit[Manual Submission]
    ManualSubmit -.-> TrackPayout
    
    TrackPayout -.-> UpdateMetrics[Update Revenue Metrics]
    Archive --> UpdateMetrics
    UpdateMetrics --> End([Process Complete])
    
    style Coordination fill:#e3f2fd,stroke-dasharray: 5 5
    style Recon fill:#e8f5e8,stroke-dasharray: 5 5
    style Analysis fill:#fff3e0,stroke-dasharray: 5 5
    style ScannerFarm fill:#f3e5f5,stroke-dasharray: 5 5
    style Exploitation fill:#ffebee,stroke-dasharray: 5 5
    style Reporting fill:#e0f2f1,stroke-dasharray: 5 5
    style HumanGate fill:#fff8e1
    style AutoSubmit fill:#f3e5f5,stroke-dasharray: 5 5
    style SubmitPlatform fill:#f3e5f5,stroke-dasharray: 5 5
    style TrackPayout fill:#f3e5f5,stroke-dasharray: 5 5
```

## 3. Activity Tracking System (GitHub Actions Style)

```mermaid
graph TB
    subgraph "Activity Lifecycle"
        ActivityCreated[Activity Created<br/>📝 Queued Status]
        ActivityStarted[Activity Started<br/>⏯️ In Progress]
        
        subgraph "Job Execution"
            Job1[Job: Reconnaissance<br/>🔍 Asset Discovery]
            Job2[Job: Analysis<br/>🧠 Vuln Detection]
            Job3[Job: Exploitation<br/>💥 PoC Generation]
            Job4[Job: Reporting<br/>📄 Documentation]
        end
        
        ActivityComplete[Activity Complete<br/>✅ Success/❌ Failed]
    end
    
    subgraph "Data Tracking"
        Logs[(Activity Logs<br/>Timestamped Messages)]
        Artifacts[(Artifacts<br/>Evidence Files)]
        Runs[(Job Runs<br/>Step Details)]
        Status[(Status Updates<br/>Real-time Progress)]
    end
    
    subgraph "UI Components"
        ActivityList[📋 Activity History List<br/>Filterable & Searchable]
        ActivityDetail[🔍 Activity Detail View<br/>Jobs, Logs, Artifacts]
        JobExpansion[📊 Job Expansion<br/>Step-by-step execution]
        ArtifactViewer[📁 Artifact Viewer<br/>Evidence inspection]
    end
    
    ActivityCreated --> Job1
    Job1 --> Job2
    Job2 --> Job3
    Job3 --> Job4
    Job4 --> ActivityComplete
    
    Job1 -.-> Logs
    Job2 -.-> Logs
    Job3 -.-> Logs
    Job4 -.-> Logs
    
    Job1 -.-> Artifacts
    Job2 -.-> Artifacts
    Job3 -.-> Artifacts
    Job4 -.-> Artifacts
    
    Job1 -.-> Runs
    Job2 -.-> Runs
    Job3 -.-> Runs
    Job4 -.-> Runs
    
    ActivityStarted -.-> Status
    ActivityComplete -.-> Status
    
    Logs --> ActivityList
    Status --> ActivityList
    ActivityList --> ActivityDetail
    ActivityDetail --> JobExpansion
    ActivityDetail --> ArtifactViewer
    Artifacts --> ArtifactViewer
```

## 4. Data Flow Architecture

```mermaid
graph LR
    subgraph "Data Sources"
        UserInput[User Actions<br/>Scan Requests]
        ClaudeFlow[Claude Flow Agents<br/>Automated Results]
        Platforms[Platform APIs<br/>Submission Status]
        Tools[Security Tools<br/>Scan Results]
    end
    
    subgraph "Data Processing"
        ActivityEngine[Activity Engine<br/>Event Processing]
        FindingProcessor[Finding Processor<br/>Vulnerability Analysis]
        ArtifactManager[Artifact Manager<br/>Evidence Handling]
        MetricsCalculator[Metrics Calculator<br/>ROI Analysis]
    end
    
    subgraph "Data Storage"
        Activities[(Activities<br/>Execution History)]
        Findings[(Findings<br/>Vulnerabilities)]
        Artifacts[(Artifacts<br/>Evidence Files)]
        Analytics[(Analytics<br/>Revenue & Performance)]
    end
    
    subgraph "Data Consumers"
        WebDashboard[Web Dashboard<br/>Real-time Visualization]
        MCPServer[MCP Server<br/>Claude Code Interface]
        Reports[Automated Reports<br/>Business Intelligence]
    end
    
    UserInput --> ActivityEngine
    ClaudeFlow -.-> FindingProcessor
    Platforms -.-> MetricsCalculator
    Tools -.-> ArtifactManager
    
    ActivityEngine -.-> Activities
    FindingProcessor -.-> Findings
    ArtifactManager -.-> Artifacts
    MetricsCalculator -.-> Analytics
    
    Activities --> WebDashboard
    Findings --> WebDashboard
    Artifacts --> WebDashboard
    Analytics --> WebDashboard
    
    Activities --> MCPServer
    Findings --> MCPServer
    Analytics --> MCPServer
    
    Analytics --> Reports
    Findings --> Reports
```

## 5. Human-in-the-Loop Integration Points

```mermaid
graph TD
    subgraph "Automated Pipeline"
        AutoScan[Automated Vulnerability Scan]
        AutoAnalysis[Automated Analysis]
        AutoPoC[Automated PoC Generation]
    end
    
    subgraph "Human Oversight Points"
        ReviewFindings{Review Findings<br/>Quality Check}
        ApproveSubmission{Approve Submission<br/>Platform Compliance}
        ValidateEvidence{Validate Evidence<br/>Proof Quality}
        AdjustSettings{Adjust Settings<br/>Rate Limits & Scope}
    end
    
    subgraph "UI Interfaces"
        WebDashboard[🌐 Web Dashboard<br/>Visual Review Interface]
        ClaudeChat[💬 Claude Code Chat<br/>Conversational Interface]
        MobileAlerts[📱 Mobile Alerts<br/>Push Notifications]
    end
    
    subgraph "Decision Support"
        RiskAssessment[Risk Assessment<br/>Impact Analysis]
        PayoutEstimate[Payout Estimation<br/>ROI Calculation]
        PlatformHistory[Platform History<br/>Success Rates]
        ComplianceCheck[Compliance Check<br/>Terms Validation]
    end
    
    AutoScan -.-> ReviewFindings
    AutoAnalysis -.-> ReviewFindings
    AutoPoC -.-> ValidateEvidence
    
    ReviewFindings -->|✅ Approve| ApproveSubmission
    ReviewFindings -->|❌ Reject| AdjustSettings
    ReviewFindings -->|🔄 Modify| AutoAnalysis
    
    ValidateEvidence -->|✅ Good| ApproveSubmission
    ValidateEvidence -->|❌ Insufficient| AutoPoC
    
    ApproveSubmission -.->|✅ Submit| AutoSubmit[Automated Submission]
    ApproveSubmission -->|❌ Hold| QueueManual[Manual Queue]
    
    WebDashboard --> ReviewFindings
    WebDashboard --> ApproveSubmission
    WebDashboard --> ValidateEvidence
    WebDashboard --> AdjustSettings
    
    ClaudeChat --> ReviewFindings
    ClaudeChat --> ApproveSubmission
    
    RiskAssessment -.-> ReviewFindings
    PayoutEstimate -.-> ApproveSubmission
    PlatformHistory -.-> ApproveSubmission
    ComplianceCheck -.-> ApproveSubmission
    
    style ReviewFindings fill:#fff3e0
    style ApproveSubmission fill:#e8f5e8
    style ValidateEvidence fill:#e3f2fd
    style AdjustSettings fill:#fce4ec
```

## 6. Claude Code MCP Integration

```mermaid
graph TB
    subgraph "Claude Code Interface"
        Chat[Natural Language Chat<br/>User Conversations]
        MCPClient[MCP Client<br/>Tool & Resource Access]
    end
    
    subgraph "MCP Server"
        Tools[MCP Tools<br/>Actions Claude Can Take]
        Resources[MCP Resources<br/>Data Claude Can Access]
    end
    
    subgraph "Available Tools"
        StartScan[start_scan<br/>Launch vulnerability scan]
        ApproveFinding[approve_finding<br/>Approve for submission]
        StopScan[stop_scan<br/>Halt running scan]
        SystemHealth[get_system_health<br/>Status overview]
        AnalyzeFinding[analyze_finding<br/>Detailed analysis]
    end
    
    subgraph "Available Resources"
        StatusResource[bugbounty://status<br/>Real-time system status]
        ProgramsResource[bugbounty://programs<br/>Available programs]
        FindingsResource[bugbounty://findings<br/>All findings + summary]
        ScansResource[bugbounty://scans<br/>Active scan statuses]
        AnalyticsResource[bugbounty://analytics<br/>Revenue & performance]
    end
    
    subgraph "Bug Bounty System"
        API[FastAPI Backend]
        Database[(Database)]
        ActivityTracker[Activity Tracker]
    end
    
    Chat --> MCPClient
    MCPClient -.-> Tools
    MCPClient -.-> Resources
    
    Tools --> API
    Resources --> API
    
    StartScan --> API
    ApproveFinding --> API
    StopScan --> API
    SystemHealth --> API
    AnalyzeFinding --> API
    
    StatusResource --> API
    ProgramsResource --> API
    FindingsResource --> API
    ScansResource --> API
    AnalyticsResource --> API
    
    API --> Database
    API --> ActivityTracker
    
    style Chat fill:#e8f5e8
    style MCPClient fill:#e3f2fd
    style Tools fill:#fff3e0
    style Resources fill:#f3e5f5
```

## 7. Deployment Architecture

```mermaid
graph TB
    subgraph "Development Environment"
        DevMachine[Developer Machine<br/>VS Code + Claude Code]
        LocalDocker[Docker Compose<br/>Local Development Stack]
    end
    
    subgraph "Container Orchestration"
        subgraph "Application Services"
            APIContainer[API Container<br/>FastAPI + Socket.IO]
            UIContainer[UI Container<br/>Nginx + React Build]
            WorkerContainer[Worker Container<br/>Background Tasks]
            MCPContainer[MCP Container<br/>Claude Code Integration]
        end
        
        subgraph "Infrastructure Services"
            PostgreSQLContainer[PostgreSQL Container<br/>Primary Database]
            RedisContainer[Redis Container<br/>Task Queue & Cache]
            MinIOContainer[MinIO Container<br/>Object Storage]
        end
    end
    
    subgraph "External Integrations"
        ClaudeFlowCloud[Claude Flow<br/>cloud.anthropic.com]
        PlatformAPIs[Platform APIs<br/>HackerOne, Bugcrowd]
        SecurityTools[Security Tools<br/>Nuclei, Burp Suite]
    end
    
    subgraph "Monitoring & Logging"
        Logs[Application Logs<br/>Structured Logging]
        Metrics[Performance Metrics<br/>Response Times, Errors]
        Alerts[Alert System<br/>Critical Issues]
    end
    
    DevMachine --> LocalDocker
    LocalDocker --> APIContainer
    LocalDocker --> UIContainer
    LocalDocker --> WorkerContainer
    LocalDocker --> MCPContainer
    
    APIContainer --> PostgreSQLContainer
    APIContainer --> RedisContainer
    APIContainer --> MinIOContainer
    WorkerContainer --> RedisContainer
    
    APIContainer -.-> ClaudeFlowCloud
    APIContainer -.-> PlatformAPIs  
    WorkerContainer -.-> SecurityTools
    
    APIContainer --> Logs
    UIContainer --> Logs
    WorkerContainer --> Logs
    
    Logs --> Metrics
    Metrics --> Alerts
    
    style DevMachine fill:#e8f5e8
    style APIContainer fill:#e3f2fd
    style UIContainer fill:#fff3e0
    style WorkerContainer fill:#f3e5f5
    style PostgreSQLContainer fill:#ffebee
    style RedisContainer fill:#fff8e1
    style MinIOContainer fill:#e0f2f1
```

## 8. Security & Compliance Flow

```mermaid
graph TD
    subgraph "Pre-Scan Validation"
        ScopeCheck[Scope Validation<br/>In-scope assets only]
        RateLimitCheck[Rate Limit Check<br/>Platform compliance]
        PermissionCheck[Permission Check<br/>Authorization valid]
    end
    
    subgraph "Safe Scanning"
        PassiveRecon[Passive Reconnaissance<br/>No intrusive testing]
        SafePoC[Safe PoC Generation<br/>No system damage]
        EvidenceCapture[Evidence Capture<br/>Proof without harm]
    end
    
    subgraph "Responsible Disclosure"
        FindingValidation[Finding Validation<br/>Eliminate false positives]
        ImpactAssessment[Impact Assessment<br/>CVSS scoring]
        ReportGeneration[Report Generation<br/>Professional documentation]
        PlatformSubmission[Platform Submission<br/>Proper channels]
    end
    
    subgraph "Compliance Monitoring"
        ActivityAudit[Activity Audit<br/>Complete tracking]
        DataProtection[Data Protection<br/>Sensitive info handling]
        RetentionPolicy[Retention Policy<br/>Evidence lifecycle]
    end
    
    ScopeCheck -.-> PassiveRecon
    RateLimitCheck -.-> PassiveRecon
    PermissionCheck -.-> PassiveRecon
    
    PassiveRecon -.-> SafePoC
    SafePoC -.-> EvidenceCapture
    
    EvidenceCapture -.-> FindingValidation
    FindingValidation -.-> ImpactAssessment
    ImpactAssessment -.-> ReportGeneration
    ReportGeneration -.-> PlatformSubmission
    
    PassiveRecon -.-> ActivityAudit
    SafePoC -.-> ActivityAudit
    EvidenceCapture -.-> DataProtection
    ReportGeneration -.-> RetentionPolicy
    
    style ScopeCheck fill:#e8f5e8
    style SafePoC fill:#fff3e0
    style FindingValidation fill:#e3f2fd
    style ActivityAudit fill:#f3e5f5
```

---

## Implementation Status Legend

**Solid lines (—)**: Fully implemented and functional
**Dotted lines (- - -)**: Not yet implemented (simulation/placeholder)
**Dashed borders**: Components that exist but need real implementation

## Current Implementation Status

### ✅ **Implemented & Working**
- **Web UI Dashboard** - Complete React interface with real-time updates
- **FastAPI Backend** - Full API with WebSocket support
- **MCP Server** - Claude Code integration with all tools/resources
- **Activity Tracking** - GitHub Actions-style workflow simulation
- **Container Infrastructure** - Docker compose with all services

### 🔄 **Partially Implemented (Simulation)**
- **Scan Orchestrator** - Framework exists, but uses hardcoded delays
- **Finding Manager** - Basic CRUD, but no real vulnerability detection
- **Evidence Store** - Structure in place, but no actual artifact generation

### ❌ **Not Yet Implemented**
- **Claude Flow Integration** - No connection to actual 6-agent pipeline
- **Bug Bounty Platform APIs** - No HackerOne/Bugcrowd integration
- **Security Tools** - No Nuclei, Burp Suite, or other scanner integration
- **Database Persistence** - Uses in-memory storage instead of PostgreSQL
- **Real Vulnerability Scanning** - All scanning is simulated

---

These diagrams provide comprehensive visualization of:

1. **System Architecture** - Overall component relationships
2. **Process Flow** - End-to-end bug bounty workflow
3. **Activity Tracking** - GitHub Actions-style execution tracking
4. **Data Flow** - Information movement through the system
5. **Human Integration** - Where human oversight is required
6. **MCP Integration** - Claude Code interface capabilities
7. **Deployment** - Container orchestration and infrastructure
8. **Security & Compliance** - Ethical and safe operation procedures

Each diagram can be rendered in any Markdown viewer that supports Mermaid, providing clear visual documentation for developers, stakeholders, and auditors.

**Development Strategy**: As components are implemented, their connecting lines should be changed from dotted (-.->)  to solid (-->) and their styling updated to remove the dashed borders.