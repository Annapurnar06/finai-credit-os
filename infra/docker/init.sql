-- FINAI Credit OS — Database Initialization
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Borrower entity graph (PostgreSQL JSONB — Neo4j replacement for M1)
CREATE TABLE IF NOT EXISTS borrower_entities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pan VARCHAR(10) UNIQUE,
    aadhaar_hash VARCHAR(64),
    mobile_hash VARCHAR(64),
    fields JSONB NOT NULL DEFAULT '{}',
    provenance JSONB NOT NULL DEFAULT '[]',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_borrower_pan ON borrower_entities(pan);
CREATE INDEX idx_borrower_aadhaar ON borrower_entities(aadhaar_hash);
CREATE INDEX idx_borrower_mobile ON borrower_entities(mobile_hash);
CREATE INDEX idx_borrower_fields ON borrower_entities USING GIN(fields);

-- Append-only audit log (Kafka replacement for M1)
CREATE TABLE IF NOT EXISTS audit_events (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    event_type VARCHAR(100) NOT NULL,
    agent_id VARCHAR(100),
    borrower_id UUID REFERENCES borrower_entities(id),
    loan_id UUID,
    application_id UUID,
    commit_class CHAR(1) NOT NULL CHECK (commit_class IN ('R', 'S', 'H', 'I')),
    input_hash VARCHAR(64),
    output_hash VARCHAR(64),
    policy_version VARCHAR(50),
    model_id VARCHAR(100),
    latency_ms INTEGER,
    trace_id VARCHAR(64),
    payload JSONB NOT NULL DEFAULT '{}'
);
CREATE INDEX idx_audit_borrower ON audit_events(borrower_id);
CREATE INDEX idx_audit_loan ON audit_events(loan_id);
CREATE INDEX idx_audit_application ON audit_events(application_id);
CREATE INDEX idx_audit_created ON audit_events(created_at);
CREATE INDEX idx_audit_type ON audit_events(event_type);

-- Loan applications
CREATE TABLE IF NOT EXISTS loan_applications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    borrower_id UUID NOT NULL REFERENCES borrower_entities(id),
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    product_type VARCHAR(50),
    requested_amount DECIMAL(15, 2),
    extraction_results JSONB NOT NULL DEFAULT '{}',
    proposal JSONB,
    eligibility JSONB,
    risk_flags JSONB NOT NULL DEFAULT '[]',
    policy_version VARCHAR(50),
    hitl_decisions JSONB NOT NULL DEFAULT '[]',
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_app_borrower ON loan_applications(borrower_id);
CREATE INDEX idx_app_status ON loan_applications(status);

-- HITL review queue
CREATE TABLE IF NOT EXISTS hitl_queue (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    application_id UUID NOT NULL REFERENCES loan_applications(id),
    action_type VARCHAR(100) NOT NULL,
    commit_class CHAR(1) NOT NULL,
    decision_brief JSONB NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'pending',
    assigned_to VARCHAR(100),
    decision JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMPTZ
);
CREATE INDEX idx_hitl_status ON hitl_queue(status);
CREATE INDEX idx_hitl_application ON hitl_queue(application_id);

-- Policy versions (for policy engine)
CREATE TABLE IF NOT EXISTS policy_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_type VARCHAR(50) NOT NULL,
    segment VARCHAR(50) NOT NULL,
    version VARCHAR(50) NOT NULL,
    effective_date TIMESTAMPTZ NOT NULL,
    rules JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (product_type, segment, version)
);

-- Prompt management (versioned system prompts)
CREATE TABLE IF NOT EXISTS prompt_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id VARCHAR(100) NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    system_prompt TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}',
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (agent_id, version)
);
