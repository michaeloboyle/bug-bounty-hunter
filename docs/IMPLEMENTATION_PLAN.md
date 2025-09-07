# Passive Scanning Pipeline - Implementation Plan

## 🎯 Implementation Strategy

This plan transforms the passive scanning design into actionable development tasks, prioritized for maximum value delivery with minimal risk.

## 📅 Development Timeline (6 Weeks)

### **Week 1-2: Foundation & Asset Discovery**
**Goal**: Build core asset discovery engine

#### **Database Models (SQLAlchemy)**
```python
# engine/models/passive_scan.py
class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    domain = Column(String, nullable=False) 
    bug_bounty_platform = Column(String)  # "hackerone", "bugcrowd"
    scope_urls = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class Asset(Base):
    __tablename__ = "assets"
    
    id = Column(String, primary_key=True)
    organization_id = Column(String, ForeignKey("organizations.id"))
    asset_type = Column(String)  # "subdomain", "ip", "url"
    value = Column(String, nullable=False)  # actual subdomain/IP
    source = Column(String)  # "crt.sh", "github", "google"
    confidence = Column(Float, default=1.0)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    
    # Technology stack info
    technologies = Column(JSON)  # [{"name": "nginx", "version": "1.18.0"}]
    http_status = Column(Integer)
    title = Column(String)
    
    # Relationships
    findings = relationship("Finding", back_populates="asset")

class Finding(Base):
    __tablename__ = "findings"
    
    id = Column(String, primary_key=True)
    asset_id = Column(String, ForeignKey("assets.id"))
    organization_id = Column(String, ForeignKey("organizations.id"))
    
    # Finding details
    vulnerability_type = Column(String)  # "info_disclosure", "auth_bypass"
    severity = Column(String)  # "critical", "high", "medium", "low"
    cvss_score = Column(Float)
    title = Column(String, nullable=False)
    description = Column(Text)
    
    # Evidence
    evidence_urls = Column(JSON)  # [{"url": "...", "type": "screenshot"}]
    evidence_text = Column(Text)
    
    # Workflow
    status = Column(String, default="new")  # "new", "validated", "submitted", "duplicate", "invalid"
    platform_submission_id = Column(String)
    payout_amount = Column(Integer)
    
    # Metadata
    detected_at = Column(DateTime, default=datetime.utcnow)
    validated_at = Column(DateTime)
    submitted_at = Column(DateTime)
```

#### **Certificate Transparency Collector**
```python
# engine/passive_scan/cert_transparency.py
import httpx
import asyncio
from typing import List, Dict

class CertificateTransparencyCollector:
    def __init__(self):
        self.sources = {
            "crt.sh": "https://crt.sh/?q={domain}&output=json",
            "certspotter": "https://api.certspotter.com/v1/issuances?domain={domain}",
            "facebook_ct": "https://graph.facebook.com/certificates?query={domain}"
        }
    
    async def collect_subdomains(self, domain: str) -> List[str]:
        """Collect subdomains from Certificate Transparency logs"""
        subdomains = set()
        
        async with httpx.AsyncClient() as client:
            tasks = [
                self._query_source(client, source, url.format(domain=domain))
                for source, url in self.sources.items()
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for source_name, result in zip(self.sources.keys(), results):
                if isinstance(result, Exception):
                    logger.error(f"Error querying {source_name}: {result}")
                    continue
                    
                source_subdomains = self._parse_ct_response(source_name, result)
                subdomains.update(source_subdomains)
        
        return list(subdomains)
    
    async def _query_source(self, client: httpx.AsyncClient, source: str, url: str) -> Dict:
        """Query a single CT source"""
        try:
            response = await client.get(url, timeout=30.0)
            response.raise_for_status()
            return {"source": source, "data": response.json()}
        except Exception as e:
            return {"source": source, "error": str(e)}
    
    def _parse_ct_response(self, source: str, response: Dict) -> List[str]:
        """Parse CT response based on source format"""
        if response.get("error"):
            return []
            
        data = response.get("data", [])
        subdomains = []
        
        if source == "crt.sh":
            for cert in data:
                name_value = cert.get("name_value", "")
                # Parse both common name and SAN entries
                names = name_value.replace("\n", ",").split(",")
                for name in names:
                    name = name.strip()
                    if name and self._is_valid_subdomain(name):
                        subdomains.append(name)
        
        elif source == "certspotter":
            for cert in data:
                dns_names = cert.get("dns_names", [])
                for name in dns_names:
                    if self._is_valid_subdomain(name):
                        subdomains.append(name)
        
        return subdomains
    
    def _is_valid_subdomain(self, name: str) -> bool:
        """Validate subdomain format"""
        if not name or name.startswith("*"):
            return False
        # Add more validation as needed
        return "." in name and len(name) > 3
```

#### **Basic Vulnerability Scanner**
```python
# engine/passive_scan/info_disclosure.py
import re
from typing import List, Dict
from .search_engines import GoogleDorker

class InformationDisclosureScanner:
    def __init__(self):
        self.patterns = {
            'exposed_git': {
                'dork': 'site:{domain} inurl:"/.git/" "parent directory"',
                'severity': 'high',
                'description': 'Exposed .git directory allows source code access'
            },
            'config_files': {
                'dork': 'site:{domain} filetype:env OR filetype:config OR filetype:ini',
                'severity': 'medium', 
                'description': 'Configuration files may contain sensitive information'
            },
            'backup_files': {
                'dork': 'site:{domain} "index of" (backup OR .bak OR .old)',
                'severity': 'medium',
                'description': 'Backup files may contain sensitive source code'
            },
            'api_documentation': {
                'dork': 'site:{domain} "swagger" OR "api-docs" OR "redoc"',
                'severity': 'low',
                'description': 'API documentation may reveal internal endpoints'
            },
            'database_files': {
                'dork': 'site:{domain} filetype:sql OR filetype:db OR "database"',
                'severity': 'high',
                'description': 'Database files may contain sensitive data'
            }
        }
        
        self.dorker = GoogleDorker()
    
    async def scan_domain(self, domain: str) -> List[Dict]:
        """Scan domain for information disclosure vulnerabilities"""
        findings = []
        
        for vuln_type, config in self.patterns.items():
            dork_query = config['dork'].format(domain=domain)
            
            try:
                results = await self.dorker.search(dork_query, max_results=10)
                
                for result in results:
                    finding = {
                        'type': 'Information Disclosure',
                        'subtype': vuln_type,
                        'severity': config['severity'],
                        'title': f"{vuln_type.replace('_', ' ').title()} - {domain}",
                        'description': config['description'],
                        'evidence_urls': [result['url']],
                        'evidence_text': result.get('snippet', ''),
                        'confidence': 0.8  # Lower confidence for dorking results
                    }
                    
                    findings.append(finding)
                    
            except Exception as e:
                logger.error(f"Error scanning {domain} for {vuln_type}: {e}")
        
        return findings
```

### **Week 3-4: Code Repository Mining**

#### **GitHub Secret Scanner**
```python
# engine/passive_scan/github_scanner.py
import httpx
import re
from typing import List, Dict, Set

class GitHubSecretScanner:
    def __init__(self, github_token: str):
        self.token = github_token
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"token {github_token}"}
        )
        
        # Common secret patterns
        self.secret_patterns = {
            'api_key': r'(?i)api[_-]?key\s*[:=]\s*["\']([a-zA-Z0-9]{20,})["\']',
            'aws_access_key': r'AKIA[0-9A-Z]{16}',
            'aws_secret_key': r'(?i)aws[_-]?secret[_-]?access[_-]?key\s*[:=]\s*["\']([a-zA-Z0-9/+=]{40})["\']',
            'database_url': r'(?i)(mysql|postgres|mongodb)://[^\s]+:[^\s]+@[^\s]+',
            'private_key': r'-----BEGIN [A-Z ]*PRIVATE KEY-----',
            'jwt_token': r'eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+',
            'slack_token': r'xox[baprs]-[a-zA-Z0-9-]+',
            'stripe_key': r'sk_live_[a-zA-Z0-9]{24}',
        }
    
    async def scan_organization(self, org_name: str) -> List[Dict]:
        """Scan all public repositories for an organization"""
        findings = []
        
        # Get all public repositories
        repos = await self._get_organization_repos(org_name)
        
        for repo in repos:
            repo_findings = await self._scan_repository(repo)
            findings.extend(repo_findings)
        
        return findings
    
    async def _get_organization_repos(self, org_name: str) -> List[Dict]:
        """Get all public repositories for an organization"""
        repos = []
        page = 1
        
        while True:
            url = f"https://api.github.com/orgs/{org_name}/repos"
            params = {"type": "public", "per_page": 100, "page": page}
            
            response = await self.client.get(url, params=params)
            
            if response.status_code != 200:
                break
                
            batch = response.json()
            if not batch:
                break
                
            repos.extend(batch)
            page += 1
        
        return repos
    
    async def _scan_repository(self, repo: Dict) -> List[Dict]:
        """Scan a single repository for secrets"""
        findings = []
        repo_name = repo['full_name']
        
        # Search code in repository
        for secret_type, pattern in self.secret_patterns.items():
            search_results = await self._search_code(repo_name, pattern)
            
            for result in search_results:
                finding = {
                    'type': 'Secret Exposure',
                    'subtype': secret_type,
                    'severity': self._get_secret_severity(secret_type),
                    'title': f"{secret_type.replace('_', ' ').title()} exposed in {repo_name}",
                    'description': f"Potential {secret_type} found in repository code",
                    'evidence_urls': [result['html_url']],
                    'evidence_text': result.get('text_matches', [{}])[0].get('fragment', ''),
                    'repository': repo_name,
                    'file_path': result['path'],
                    'confidence': 0.9
                }
                
                findings.append(finding)
        
        return findings
    
    async def _search_code(self, repo_name: str, pattern: str) -> List[Dict]:
        """Search for code patterns in repository"""
        # GitHub Code Search API
        url = "https://api.github.com/search/code"
        params = {
            "q": f"repo:{repo_name} {pattern}",
            "per_page": 10
        }
        
        try:
            response = await self.client.get(url, params=params)
            
            if response.status_code == 200:
                return response.json().get('items', [])
            else:
                logger.warning(f"GitHub search failed for {repo_name}: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error searching GitHub for {repo_name}: {e}")
            return []
    
    def _get_secret_severity(self, secret_type: str) -> str:
        """Determine severity based on secret type"""
        high_severity = ['aws_access_key', 'aws_secret_key', 'private_key', 'database_url']
        medium_severity = ['api_key', 'jwt_token', 'slack_token', 'stripe_key']
        
        if secret_type in high_severity:
            return 'high'
        elif secret_type in medium_severity:
            return 'medium'
        else:
            return 'low'
```

### **Week 5-6: Advanced Analysis & Integration**

#### **Cloud Storage Scanner**
```python
# engine/passive_scan/cloud_storage.py
import httpx
import asyncio
from typing import List, Dict

class CloudStorageScanner:
    def __init__(self):
        self.cloud_patterns = {
            'aws_s3': {
                'pattern': r's3\.amazonaws\.com/([a-zA-Z0-9\-\.]+)',
                'check_url': 'https://{bucket}.s3.amazonaws.com/',
                'list_url': 'https://{bucket}.s3.amazonaws.com/?list-type=2'
            },
            'gcp_storage': {
                'pattern': r'storage\.googleapis\.com/([a-zA-Z0-9\-\.]+)',
                'check_url': 'https://storage.googleapis.com/{bucket}/',
                'list_url': 'https://storage.googleapis.com/storage/v1/b/{bucket}/o'
            },
            'azure_blob': {
                'pattern': r'([a-zA-Z0-9]+)\.blob\.core\.windows\.net',
                'check_url': 'https://{bucket}.blob.core.windows.net/',
                'list_url': 'https://{bucket}.blob.core.windows.net/?comp=list'
            }
        }
    
    async def scan_organization_storage(self, org_name: str) -> List[Dict]:
        """Scan for exposed cloud storage buckets"""
        findings = []
        
        # First, find potential bucket names from various sources
        bucket_candidates = await self._find_bucket_names(org_name)
        
        # Test each candidate for public access
        async with httpx.AsyncClient() as client:
            for bucket_name, cloud_type in bucket_candidates:
                exposure = await self._check_bucket_exposure(client, bucket_name, cloud_type)
                
                if exposure:
                    finding = {
                        'type': 'Cloud Misconfiguration',
                        'subtype': f'Public {cloud_type.upper()} Bucket',
                        'severity': 'high',
                        'title': f'Publicly accessible {cloud_type} bucket: {bucket_name}',
                        'description': f'Cloud storage bucket allows public access',
                        'evidence_urls': [exposure['url']],
                        'evidence_text': exposure['evidence'],
                        'bucket_name': bucket_name,
                        'cloud_provider': cloud_type,
                        'confidence': 0.95
                    }
                    
                    findings.append(finding)
        
        return findings
    
    async def _find_bucket_names(self, org_name: str) -> List[tuple]:
        """Find potential bucket names from various sources"""
        candidates = []
        
        # Common naming patterns
        common_suffixes = ['', '-dev', '-prod', '-staging', '-backup', '-static', '-assets']
        
        for suffix in common_suffixes:
            bucket_name = f"{org_name.lower()}{suffix}"
            candidates.extend([
                (bucket_name, 'aws_s3'),
                (bucket_name, 'gcp_storage'), 
                (bucket_name, 'azure_blob')
            ])
        
        # TODO: Add GitHub repository scanning for bucket references
        # TODO: Add Google dorking for bucket URLs
        
        return candidates
    
    async def _check_bucket_exposure(self, client: httpx.AsyncClient, bucket_name: str, cloud_type: str) -> Dict:
        """Check if a bucket allows public access"""
        config = self.cloud_patterns[cloud_type]
        
        try:
            # Test basic access
            check_url = config['check_url'].format(bucket=bucket_name)
            response = await client.get(check_url, timeout=10.0)
            
            if response.status_code == 200:
                # Try to list contents
                list_url = config['list_url'].format(bucket=bucket_name)
                list_response = await client.get(list_url, timeout=10.0)
                
                if list_response.status_code == 200:
                    return {
                        'url': list_url,
                        'evidence': f'Bucket listing successful: {len(list_response.content)} bytes'
                    }
                else:
                    return {
                        'url': check_url,
                        'evidence': 'Bucket accessible but listing restricted'
                    }
                    
        except Exception as e:
            logger.debug(f"Error checking bucket {bucket_name}: {e}")
        
        return None
```

## 🔧 API Integration Points

### **FastAPI Endpoints**
```python
# engine/api/passive_scan.py
from fastapi import APIRouter, Depends, BackgroundTasks
from ..models.passive_scan import Organization, Asset, Finding
from ..passive_scan.orchestrator import PassiveScanOrchestrator

router = APIRouter(prefix="/passive-scan", tags=["passive-scan"])

@router.post("/organizations/{org_id}/scan")
async def start_passive_scan(
    org_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Start a passive scan for an organization"""
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(404, "Organization not found")
    
    # Start background scan
    orchestrator = PassiveScanOrchestrator(db)
    background_tasks.add_task(orchestrator.run_full_scan, org_id)
    
    return {"status": "started", "organization": org.name}

@router.get("/organizations/{org_id}/assets")
async def get_organization_assets(
    org_id: str,
    asset_type: str = None,
    db: Session = Depends(get_db)
):
    """Get all assets discovered for an organization"""
    query = db.query(Asset).filter(Asset.organization_id == org_id)
    
    if asset_type:
        query = query.filter(Asset.asset_type == asset_type)
    
    assets = query.order_by(Asset.last_seen.desc()).all()
    
    return {
        "assets": [
            {
                "id": asset.id,
                "type": asset.asset_type,
                "value": asset.value,
                "technologies": asset.technologies,
                "confidence": asset.confidence,
                "first_seen": asset.first_seen,
                "findings_count": len(asset.findings)
            }
            for asset in assets
        ]
    }

@router.get("/findings")
async def get_findings(
    organization_id: str = None,
    severity: str = None,
    status: str = None,
    db: Session = Depends(get_db)
):
    """Get findings with filters"""
    query = db.query(Finding)
    
    if organization_id:
        query = query.filter(Finding.organization_id == organization_id)
    if severity:
        query = query.filter(Finding.severity == severity)
    if status:
        query = query.filter(Finding.status == status)
    
    findings = query.order_by(Finding.detected_at.desc()).limit(100).all()
    
    return {"findings": findings}
```

## 📊 Monitoring & Quality Assurance

### **Confidence Scoring System**
```python
# engine/passive_scan/confidence.py
class ConfidenceScorer:
    def __init__(self):
        self.source_weights = {
            'crt.sh': 0.9,          # High confidence in CT logs
            'github': 0.8,          # Code repos are reliable
            'google_dork': 0.6,     # Search results can be noisy
            'subdomain_brute': 0.4, # Brute force less reliable
        }
        
        self.vuln_type_weights = {
            'secret_exposure': 0.9,     # Secrets are usually clear
            'exposed_git': 0.95,        # .git exposure is definitive
            'info_disclosure': 0.7,     # May be intended behavior
            'cloud_misconfiguration': 0.85,  # Usually clear misconfiguration
        }
    
    def calculate_finding_confidence(self, finding: Dict) -> float:
        """Calculate confidence score for a finding"""
        base_confidence = 0.5
        
        # Source reliability
        source = finding.get('source', 'unknown')
        source_weight = self.source_weights.get(source, 0.3)
        
        # Vulnerability type clarity
        vuln_type = finding.get('subtype', 'unknown')
        vuln_weight = self.vuln_type_weights.get(vuln_type, 0.5)
        
        # Evidence quality
        evidence_score = self._score_evidence(finding)
        
        # Calculate weighted confidence
        confidence = (
            base_confidence * 0.2 +
            source_weight * 0.3 +
            vuln_weight * 0.3 +
            evidence_score * 0.2
        )
        
        return min(confidence, 1.0)
    
    def _score_evidence(self, finding: Dict) -> float:
        """Score the quality of evidence"""
        evidence_urls = finding.get('evidence_urls', [])
        evidence_text = finding.get('evidence_text', '')
        
        score = 0.5
        
        # URL evidence
        if evidence_urls:
            score += 0.2
            
        # Text evidence quality
        if evidence_text:
            if len(evidence_text) > 100:
                score += 0.2
            if any(keyword in evidence_text.lower() for keyword in ['password', 'key', 'secret', 'token']):
                score += 0.1
        
        return min(score, 1.0)
```

## 🚀 Deployment Configuration

### **Docker Services Update**
```yaml
# Add to docker-compose.yml
services:
  passive-scanner:
    build:
      context: .
      dockerfile: Dockerfile.passive-scanner
    container_name: bbops-passive-scanner
    environment:
      - GITHUB_TOKEN=${GITHUB_TOKEN}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - VIRUSTOTAL_API_KEY=${VIRUSTOTAL_API_KEY}
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/bbops
    depends_on:
      - db
      - redis
    volumes:
      - ./engine/passive_scan:/app/passive_scan:ro
    restart: unless-stopped
    
  scheduler:
    build:
      context: .
      dockerfile: Dockerfile.scheduler
    container_name: bbops-scheduler
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/bbops
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    restart: unless-stopped
```

## 📋 Implementation Checklist

### **Phase 1 Tasks** ✅
- [ ] Set up SQLAlchemy models for passive scanning
- [ ] Implement Certificate Transparency collector
- [ ] Create basic information disclosure scanner
- [ ] Build asset inventory system
- [ ] Add passive scan API endpoints
- [ ] Create simple web interface for viewing results

### **Phase 2 Tasks** 🔄
- [ ] Implement GitHub secret scanner
- [ ] Add search engine dorking automation
- [ ] Create confidence scoring system
- [ ] Build finding deduplication
- [ ] Add automated report generation

### **Phase 3 Tasks** ⏳
- [ ] Implement cloud storage scanner
- [ ] Add third-party vulnerability correlation
- [ ] Create continuous monitoring system
- [ ] Build platform-specific submission formatting
- [ ] Add comprehensive testing and quality assurance

### **Success Criteria**
- **Week 2**: Discover 100+ subdomains for test organization
- **Week 4**: Find 5+ information disclosure issues via automation
- **Week 6**: Generate first professional bug bounty report

This implementation plan provides a clear roadmap for building a legally safe, technically sound passive reconnaissance system that delivers real value in bug bounty operations.