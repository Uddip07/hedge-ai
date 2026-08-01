export type RecommendationType = 'BUY' | 'SELL' | 'HOLD' | 'STRONG_BUY' | 'STRONG_SELL';

export interface RootResponse {
  application: string;
  version: string;
  status: string;
}

export interface HealthResponse {
  status: string;
  database: string;
  cache: string;
  application: string;
}

export interface VersionResponse {
  name: string;
  version: string;
  environment: string;
  build: {
    python_version: string;
    architecture: string;
    release_candidate?: string;
  };
}

export interface MarketQuote {
  ticker: string;
  symbol: string;
  exchange: string;
  price: string;
  currency: string;
  company_name: string;
  sector: string;
  industry: string;
  is_market_open: boolean;
  change_percent?: number;
  volume?: number;
}

export interface AnalyzeStockRequest {
  ticker: string;
  portfolio_id?: string | null;
  investment_horizon_days?: number;
}

export interface AnalyzeStockResponse {
  ticker: string;
  recommendation: string;
  consensus_score: number;
  risk_level: string;
  is_suitable_for_portfolio: boolean;
  reasoning_summary: string;
  analyzed_at: string;
}

export interface EvaluateCommitteeRequest {
  ticker: string;
  horizon: 'INTRADAY' | 'DAILY' | 'SWING' | 'LONG_TERM';
  style: 'VALUE' | 'GROWTH' | 'QUANTITATIVE' | 'TECHNICAL' | 'BALANCED';
  user_query?: string;
}

export interface EvaluateCommitteeResponse {
  decision_id: string;
  session_id: string;
  ticker: string;
  winning_recommendation: string;
  consensus_score: number;
  confidence: number;
  agreement_ratio: number;
  verdict_summary: string;
  audit_signature: string;
  timestamp: string;
  explanation: Record<string, any>;
}

export interface CompanyIntelligenceResponse {
  ticker: string;
  company_name: string;
  session_id: string;
  timestamp: string;
  executive_summary: Record<string, any>;
  market_snapshot: Record<string, any>;
  financial_highlights: Record<string, any>;
  technical_analysis: Record<string, any>;
  news_section: Record<string, any>;
  corporate_actions: Record<string, any>;
  macro_context: Record<string, any>;
  agent_opinions: Record<string, any>;
  consensus_decision: Record<string, any>;
  explainability: Record<string, any>;
  bull_case: string[];
  bear_case: string[];
}

export interface ApiCallLog {
  id: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  endpoint: string;
  status: number | 'ERR';
  latencyMs: number;
  responseSizeBytes: number;
  timestamp: string;
  requestBody?: any;
  responseBody?: any;
  error?: string;
}
