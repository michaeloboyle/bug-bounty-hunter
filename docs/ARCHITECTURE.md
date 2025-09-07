# Bug Bounty Operations - Safe Automation Architecture

This document provides visual diagrams of the safe automated intelligence collection system architecture, process flows, and data relationships using Mermaid.

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
        AutomationEngine[Safe Automation Engine<br/>CT Logs + Rate Limited APIs]
        PatternAnalysis[AI Pattern Analysis<br/>Correlation & Detection]
        ResearchAssistant[Research Assistant<br/>Human-AI Collaboration]
    end
    
    subgraph "External Systems"
        CTLogs[Certificate Transparency Logs<br/>High-Frequency Automated]
        RateLimitedAPIs[Rate Limited APIs<br/>Shodan, VirusTotal, Censys]
        ManualResearch[Manual Research Sources<br/>GitHub, Google - Human Only]
        Platforms[Bug Bounty Platforms<br/>HackerOne, Bugcrowd]
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
    FastAPI --> AutomationEngine
    FastAPI --> PatternAnalysis
    FastAPI --> ResearchAssistant
    
    AutomationEngine --> CTLogs
    AutomationEngine -.-> RateLimitedAPIs
    PatternAnalysis --> ResearchAssistant
    ResearchAssistant -.-> ManualResearch
    ResearchAssistant -.-> Platforms
    
    ActivityTracker --> PostgreSQL
    AutomationEngine -.-> PostgreSQL
    PatternAnalysis -.-> PostgreSQL
    AutomationEngine --> Redis
    ResearchAssistant -.-> MinIO
    
    style WebUI fill:#e1f5fe
    style ClaudeCode fill:#e8f5e8
    style FastAPI fill:#fff3e0
    style ActivityTracker fill:#fff3e0
    style AutomationEngine fill:#e8f5e8
    style PatternAnalysis fill:#fff3e0
    style ResearchAssistant fill:#e3f2fd
    style CTLogs fill:#e8f5e8
    style RateLimitedAPIs fill:#fff8e1,stroke-dasharray: 5 5
    style ManualResearch fill:#ffebee,stroke-dasharray: 5 5
    style Platforms fill:#f3e5f5,stroke-dasharray: 5 5
    style PostgreSQL fill:#ffebee,stroke-dasharray: 5 5
    style Redis fill:#fff8e1
    style MinIO fill:#e0f2f1,stroke-dasharray: 5 5
```

## 2. Safe Automation Process Flow

```mermaid
flowchart TD
    Start([User Initiates Intelligence Collection]) --> ProgramSelect[Select Bug Bounty Program]
    ProgramSelect --> CreateActivity[Create Activity Record]
    
    CreateActivity --> InitAutomation[Initialize Safe Automation]
    
    subgraph "High-Frequency Automation (24/7)"
        CTMonitor[🔄 CT Log Monitor<br/>15-minute intervals]
        DataProcessor[⚡ Data Processing<br/>Continuous analysis]
        PatternDetection[🧠 AI Pattern Detection<br/>Real-time correlation]
        AlertGeneration[🚨 Alert Generation<br/>Prioritized research leads]
    end
    
    subgraph "Rate-Limited APIs (Respectful)"
        ShodanEnrichment[🌐 Shodan API<br/>1 query/minute]
        VirusTotalCheck[🔍 VirusTotal API<br/>4 queries/minute]  
        CensysLookup[📊 Censys API<br/>Per subscription limit]
    end
    
    subgraph "Human-AI Collaboration"
        ResearchLeads[📋 Research Lead Review<br/>Human evaluates priorities]
        ManualSearch[🔎 Manual Investigation<br/>GitHub, Google searches]
        AIAnalysis[🤖 AI-Assisted Analysis<br/>Pattern correlation]
        EvidenceCompilation[📁 Evidence Compilation<br/>Automated organization]
    end
    
    InitAutomation --> CTMonitor
    CTMonitor --> DataProcessor
    DataProcessor --> PatternDetection
    PatternDetection --> AlertGeneration
    
    AlertGeneration --> ResearchLeads
    ResearchLeads -->|High Priority| ManualSearch
    ResearchLeads -->|Low Priority| QueueLater[Queue for Later]
    
    ManualSearch --> AIAnalysis
    AIAnalysis --> EvidenceCompilation
    
    DataProcessor -.-> ShodanEnrichment
    DataProcessor -.-> VirusTotalCheck
    DataProcessor -.-> CensysLookup
    
    ShodanEnrichment --> PatternDetection
    VirusTotalCheck --> PatternDetection
    CensysLookup --> PatternDetection
    
    EvidenceCompilation --> HumanGate{Human Review & Approval}
    
    HumanGate -->|✅ Approved| SubmitPrep[Prepare Submission]
    HumanGate -->|❌ Rejected| Archive[Archive Finding]
    HumanGate -->|🔄 Needs More Research| ManualSearch
    
    SubmitPrep --> ManualSubmit[Manual Platform Submission]
    ManualSubmit -.-> TrackPayout[Track Payout Status]
    
    TrackPayout -.-> UpdateMetrics[Update Success Metrics]
    Archive --> UpdateMetrics
    UpdateMetrics --> End([Process Complete])
    
    style CTMonitor fill:#e8f5e8
    style DataProcessor fill:#e3f2fd
    style PatternDetection fill:#fff3e0
    style AlertGeneration fill:#fff8e1
    style ShodanEnrichment fill:#fff8e1,stroke-dasharray: 5 5
    style VirusTotalCheck fill:#fff8e1,stroke-dasharray: 5 5
    style CensysLookup fill:#fff8e1,stroke-dasharray: 5 5
    style ResearchLeads fill:#ffebee
    style ManualSearch fill:#ffebee,stroke-dasharray: 5 5
    style AIAnalysis fill:#e3f2fd
    style HumanGate fill:#fff8e1
    style ManualSubmit fill:#ffebee,stroke-dasharray: 5 5
    style TrackPayout fill:#f3e5f5,stroke-dasharray: 5 5
```

## 3. Activity Tracking System (GitHub Actions Style)

```mermaid
graph TB
    subgraph "Activity Lifecycle"
        ActivityCreated[Activity Created<br/>📝 Queued Status]
        ActivityStarted[Activity Started<br/>⏯️ In Progress]
        
        subgraph "Job Execution"
            Job1[Job: CT Monitoring<br/>🔄 Certificate Transparency]
            Job2[Job: Data Processing<br/>⚡ Pattern Analysis]
            Job3[Job: Research Leads<br/>📋 Human Investigation]
            Job4[Job: Evidence Compilation<br/>📁 Automated Organization]
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

### 🔄 **Ready for Safe Implementation**
- **CT Log Monitor** - Framework exists, needs real CT API integration
- **Pattern Analysis Engine** - Basic structure in place, needs AI correlation
- **Research Assistant Interface** - UI framework exists, needs AI suggestions
- **Rate Limiting System** - Framework in place, needs API integration

### ❌ **Not Yet Implemented (Safe Automation Components)**
- **Certificate Transparency Integration** - No real CT log processing
- **Respectful API Manager** - No rate-limited API calls (Shodan, VirusTotal)
- **AI Pattern Detection** - No automated vulnerability pattern recognition
- **Manual Research Workflow** - No human-AI collaboration interface
- **Evidence Compilation System** - No automated finding organization

---

These diagrams provide comprehensive visualization of:

1. **Safe Automation Architecture** - CT logs, rate-limited APIs, AI processing
2. **Intelligence Collection Flow** - High-frequency automation with human oversight
3. **Activity Tracking** - GitHub Actions-style execution tracking
4. **Data Flow** - Information movement through safe processing pipeline
5. **Human-AI Collaboration** - Where manual research is required
6. **MCP Integration** - Claude Code interface capabilities
7. **Deployment** - Container orchestration and infrastructure
8. **Legal Compliance** - Safe automation boundaries and audit trails

Each diagram can be rendered in any Markdown viewer that supports Mermaid, providing clear visual documentation for developers, stakeholders, and compliance auditors.

**Implementation Priority**: 
1. **Green components** (CT logs, AI processing) - Safe for high-frequency automation
2. **Yellow components** (rate-limited APIs) - Implement with careful rate limiting
3. **Red components** (manual research) - Human-initiated only, no automation