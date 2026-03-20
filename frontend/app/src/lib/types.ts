export type ApplicationStatus =
  | "draft"
  | "documents_submitted"
  | "extracting"
  | "extraction_complete"
  | "proposal_generated"
  | "eligible"
  | "ineligible"
  | "hitl_pending"
  | "approved"
  | "rejected";

export type RiskLevel = "RED" | "AMBER" | "GREEN";

export type ExtractionStatus = "success" | "failure" | "low_confidence";

export type CustomerSegment =
  | "salaried"
  | "self_employed"
  | "msme"
  | "agriculture"
  | "gig_worker";

export type ProductType =
  | "personal_loan"
  | "business_loan"
  | "lap"
  | "gold_loan"
  | "agriculture_loan"
  | "vehicle_loan";

export interface RiskFlag {
  flag_id: string;
  category: string;
  level: RiskLevel;
  description: string;
  source_agent: string;
  details?: Record<string, unknown>;
}

export interface ExtractionResult {
  agent_name: string;
  doc_type: string;
  status: ExtractionStatus;
  confidence: number;
  data: Record<string, unknown>;
  errors?: string[];
}

export interface IncomeSource {
  source: string;
  monthly?: number;
  annual?: number;
  confidence: number;
  turnover_12m?: number;
  estimated_monthly_profit?: number;
}

export interface BorrowerProfile {
  borrower_name: string;
  pan: string;
  age: number;
  monthly_income: number;
  annual_income: number;
  employer: string;
  segment: CustomerSegment;
  income_sources: IncomeSource[];
  assets: Record<string, unknown>;
  liabilities: {
    bureau_score?: number;
    active_tradelines?: number;
    total_outstanding?: number;
    total_emi?: number;
  };
}

export interface EligibilityResult {
  is_eligible: boolean;
  eligible_products: Array<{ product: string; segment: string }>;
  max_loan_amount: number;
  min_loan_amount: number;
  rate_band: Record<string, number>;
  tenure_options: number[];
  rejection_reasons: string[];
  policy_version: string;
}

export interface DBRResult {
  total_monthly_emi: number;
  net_monthly_income: number;
  dbr_ratio: number;
  max_eligible_emi: number;
  active_loans?: Array<Record<string, unknown>>;
  flags: string[];
}

export interface TriangulationResult {
  declared_income: number;
  verified_income: number;
  income_confidence: number;
  sources_checked: string[];
  discrepancies: Array<{ type: string; deviation: string; sources: unknown[] }>;
}

export interface DocCheckResult {
  required: string[];
  present: string[];
  successful: string[];
  missing: string[];
  failed_extraction: string[];
  complete: boolean;
}

export interface Proposal {
  borrower_profile: BorrowerProfile;
  eligibility: EligibilityResult;
  dbr: DBRResult;
  roi: { annual_income: number; requested_amount: number; roi_ratio: number; flags: string[] };
  triangulation: TriangulationResult;
  doc_check: DocCheckResult;
}

export interface DecisionBrief {
  summary: {
    total_documents_processed: number;
    risk_assessment: string;
    red_flags_count: number;
    amber_flags_count: number;
  };
  extraction_highlights: Record<string, { status: string; confidence: number }>;
  proposal: Proposal | null;
  risk_flags: RiskFlag[];
  policy_version: string;
  review_required_because: string[];
}

export interface ApplicationResult {
  application_id: string;
  borrower_id: string;
  status: ApplicationStatus;
  auto_approve_eligible: boolean;
  extraction_results: Record<string, ExtractionResult>;
  proposal: Proposal;
  risk_flags: RiskFlag[];
  policy_version: string;
  decision_brief: DecisionBrief;
  hitl_required: boolean;
  final_decision?: string;
}

export interface ApplicationListItem {
  application_id: string;
  borrower_pan: string;
  status: ApplicationStatus;
  product_type: ProductType;
}

export interface ApplicationDetail {
  application_id: string;
  borrower_pan: string;
  product_type: ProductType;
  status: ApplicationStatus;
  result: ApplicationResult | null;
}

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  llm_mode: "mock" | "live";
  memory_mode: "in_memory" | "mem0";
}

export interface LLMHealthResponse {
  status: string;
  stats: {
    total_calls: number;
    total_tokens: number;
    mode: string;
  };
}
