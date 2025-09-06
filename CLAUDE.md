# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Automated bug bounty hunting and fixing system designed for profit maximization. This project combines AI-powered vulnerability discovery with automated exploitation proof-of-concept generation and patch development.

**Core Revenue Streams:**
1. **Platform Bug Bounties**: HackerOne, Bugcrowd, YesWeHack automated submissions
2. **AI Model Jailbreaks**: Anthropic bounties (up to $25,000) through systematic prompt injection testing
3. **Zero-Day Discovery**: High-value vulnerability identification in popular open-source projects
4. **Patch Development**: Automated fix generation for discovered vulnerabilities

## Development Setup

**Core Technologies:**
- **Python**: Primary language for AI-powered scanning, LLM integration, and automation
- **Go**: High-performance network scanners and concurrent vulnerability testing
- **JavaScript/Node.js**: Web application testing, browser automation, DOM manipulation
- **Docker**: Isolated testing environments and scalable deployment

**Key Dependencies:**
- **LangChain/OpenAI**: AI-powered code analysis and vulnerability identification
- **Nuclei**: Template-based vulnerability scanner integration
- **Selenium/Playwright**: Automated web application testing
- **SQLMap**: Automated SQL injection testing
- **Nmap**: Network discovery and service enumeration

## Automated Hunting Strategy

### High-Value Targets (ROI-Optimized)
- **Fortune 500 Companies**: $10,000-$100,000+ payouts for critical vulnerabilities
- **Crypto/DeFi Platforms**: $50,000-$1M+ for smart contract exploits
- **AI/ML Services**: $5,000-$25,000 for model bypasses and data leaks
- **Cloud Providers**: $20,000-$100,000+ for infrastructure vulnerabilities

### Platform Automation
- **HackerOne API**: Automated submission and status tracking
- **Bugcrowd Integration**: Bulk program enrollment and reporting
- **Custom Dashboards**: ROI tracking, payout analysis, success metrics
- **Duplicate Detection**: Avoid wasted effort on known issues

## Automation Pipeline

### Discovery Phase
1. **Target Enumeration**: Automated scope analysis from bug bounty programs
2. **Asset Discovery**: Subdomain enumeration, port scanning, service fingerprinting
3. **Technology Stack Analysis**: Framework detection, version identification, dependency mapping

### Vulnerability Detection
1. **Static Analysis**: AI-powered code review of open-source targets
2. **Dynamic Testing**: Automated web app scanning with custom payloads
3. **API Security**: GraphQL introspection, REST endpoint fuzzing, authentication bypasses
4. **Infrastructure Testing**: Cloud misconfigurations, container escapes, privilege escalation

### Exploitation & Reporting
1. **PoC Generation**: Automated exploit development and impact demonstration
2. **Report Creation**: AI-generated technical reports with CVSS scoring
3. **Submission Automation**: Direct API integration with bounty platforms
4. **Follow-up Management**: Automated communication with security teams

## Project Structure (To Be Established)

```
/core/                # Core automation engine and orchestration
/scanners/           # Vulnerability detection modules
  /web/              # Web application security scanners
  /api/              # API testing and fuzzing tools
  /infrastructure/   # Cloud and network security tools
  /mobile/           # Mobile application security testing
/exploits/           # PoC generation and exploitation tools
/ai/                 # LLM integration and AI-powered analysis
/platforms/          # Bug bounty platform integrations
  /hackerone/        # HackerOne API integration
  /bugcrowd/         # Bugcrowd automation
  /intigriti/        # Intigriti platform tools
/reporting/          # Automated report generation
/dashboard/          # ROI tracking and analytics
/data/               # Target databases and reconnaissance data
```

## Success Metrics

- **Monthly Revenue**: Target $10,000+ from automated discoveries
- **Submission Rate**: 100+ vulnerability reports per month
- **Success Rate**: 15%+ acceptance rate on submissions
- **Time to Discovery**: <24 hours from target identification to vulnerability confirmation

## Development Commands

Since this is a new repository, specific build/test commands will be established as the project develops. Expected patterns:

```bash
# Setup and installation
make setup              # Install dependencies and configure environment
make docker-build       # Build containerized scanning environment

# Core operations
make hunt               # Run automated vulnerability discovery
make analyze TARGET=url # Analyze specific target for vulnerabilities
make exploit CVE=id     # Generate PoC for discovered vulnerability

# Platform operations
make sync-programs      # Update bug bounty program databases
make submit-reports     # Batch submit pending vulnerability reports
make track-payouts      # Update payout status and calculate ROI

# Testing and validation
make test              # Run automated test suite
make validate-exploits # Test PoC reliability
make benchmark         # Performance testing for scanners
```

## Git Workflow

- Commit frequently with descriptive messages
- Always test tools in isolated environments
- Never commit actual vulnerability data or target-specific information
- Use feature branches for new scanner modules