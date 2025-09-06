-- Initialize bug bounty database schema
-- This file is run automatically when the PostgreSQL container starts

-- Create basic tables for future database persistence
-- Currently using in-memory data structures, but this prepares for production

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Programs table
CREATE TABLE IF NOT EXISTS programs (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    payout_max INTEGER NOT NULL,
    rps DECIMAL(3,2) NOT NULL,
    auto_ok BOOLEAN NOT NULL DEFAULT FALSE,
    triage_days INTEGER NOT NULL,
    asset_count INTEGER NOT NULL,
    tags TEXT[] NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Findings table  
CREATE TABLE IF NOT EXISTS findings (
    id VARCHAR(255) PRIMARY KEY,
    program_id VARCHAR(255) NOT NULL REFERENCES programs(id),
    type VARCHAR(100) NOT NULL,
    severity DECIMAL(3,1) NOT NULL,
    status VARCHAR(50) NOT NULL,
    payout_est INTEGER NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    evidence TEXT[] NOT NULL DEFAULT '{}',
    activity_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Activities table
CREATE TABLE IF NOT EXISTS activities (
    id VARCHAR(255) PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    program_id VARCHAR(255) REFERENCES programs(id),
    triggered_by VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE,
    duration INTEGER,
    conclusion VARCHAR(50),
    artifacts TEXT[] NOT NULL DEFAULT '{}',
    run_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Activity runs table
CREATE TABLE IF NOT EXISTS activity_runs (
    id VARCHAR(255) PRIMARY KEY,
    activity_id VARCHAR(255) NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
    job_name VARCHAR(100) NOT NULL,
    step_name VARCHAR(255),
    status VARCHAR(50) NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE,
    duration INTEGER,
    conclusion VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Activity logs table
CREATE TABLE IF NOT EXISTS activity_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    activity_id VARCHAR(255) NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
    run_id VARCHAR(255) REFERENCES activity_runs(id) ON DELETE SET NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    level VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Artifacts table
CREATE TABLE IF NOT EXISTS artifacts (
    id VARCHAR(255) PRIMARY KEY,
    activity_id VARCHAR(255) NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
    run_id VARCHAR(255) REFERENCES activity_runs(id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    size INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_findings_program_id ON findings(program_id);
CREATE INDEX IF NOT EXISTS idx_findings_status ON findings(status);
CREATE INDEX IF NOT EXISTS idx_findings_timestamp ON findings(timestamp);
CREATE INDEX IF NOT EXISTS idx_activities_program_id ON activities(program_id);
CREATE INDEX IF NOT EXISTS idx_activities_status ON activities(status);
CREATE INDEX IF NOT EXISTS idx_activities_start_time ON activities(start_time);
CREATE INDEX IF NOT EXISTS idx_activity_runs_activity_id ON activity_runs(activity_id);
CREATE INDEX IF NOT EXISTS idx_activity_logs_activity_id ON activity_logs(activity_id);
CREATE INDEX IF NOT EXISTS idx_artifacts_activity_id ON artifacts(activity_id);

-- Comments for documentation
COMMENT ON TABLE programs IS 'Bug bounty programs available for scanning';
COMMENT ON TABLE findings IS 'Discovered vulnerabilities and their status';
COMMENT ON TABLE activities IS 'GitHub Actions-style activity tracking';
COMMENT ON TABLE activity_runs IS 'Individual jobs within activities';
COMMENT ON TABLE activity_logs IS 'Detailed logs for activities and runs';
COMMENT ON TABLE artifacts IS 'Evidence files, reports, and screenshots';

-- Grant permissions (for production, use more restrictive permissions)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;