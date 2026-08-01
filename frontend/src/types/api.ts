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
  price: string | number;
  currency: string;
  company_name: string;
  sector: string;
  industry: string;
  is_market_open: boolean;
  change_percent?: number;
  change?: number;
  volume?: number;
  high?: number;
  low?: number;
}

export interface LiveTickerItem {
  ticker: string;
  name: string;
  price: number;
  change: number;
  change_percent: number;
  volume: number;
  high: number;
  low: number;
  price_change?: number;
  direction?: 'up' | 'down' | 'flat';
}

export type WsMessageType = 'SNAPSHOT' | 'TICK' | 'PING' | 'PONG' | 'SUBSCRIBE' | 'SUBSCRIBED';

export interface WsMessagePayload {
  type: WsMessageType;
  timestamp: string;
  data?: LiveTickerItem | LiveTickerItem[];
  tickers?: string[];
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

export interface AgentSignal {
  agent: string;
  recommendation: RecommendationType;
  confidence: number;
  reasoning: string;
}

export interface EvaluateCommitteeResponse {
  decision_id: string;
  session_id: string;
  ticker: string;
  winning_recommendation: RecommendationType;
  consensus_score: number;
  confidence: number;
  agreement_ratio: number;
  verdict_summary: string;
  audit_signature: string;
  timestamp: string;
  explanation: Record<string, unknown>;
  signals?: AgentSignal[];
}

export interface CompanyIntelligenceResponse {
  ticker: string;
  company_name: string;
  session_id: string;
  timestamp: string;
  executive_summary: Record<string, unknown>;
  market_snapshot: Record<string, unknown>;
  financial_highlights: Record<string, unknown>;
  technical_analysis: Record<string, unknown>;
  news_section: Record<string, unknown>;
  corporate_actions: Record<string, unknown>;
  macro_context: Record<string, unknown>;
  agent_opinions: Record<string, unknown>;
  consensus_decision: Record<string, unknown>;
  explainability: Record<string, unknown>;
  bull_case: string[];
  bear_case: string[];
}

export interface PortfolioHolding {
  symbol: string;
  company_name: string;
  quantity: number;
  average_price: number;
  current_price: number;
  total_value: number;
  unrealized_pnl: number;
  unrealized_pnl_percent: number;
  allocation_percent: number;
  sector: string;
}

export interface RiskMetrics {
  sharpe_ratio: number;
  sortino_ratio: number;
  value_at_risk_95: number;
  max_drawdown_percent: number;
  beta: number;
  alpha: number;
  volatility_annualized: number;
  leverage_ratio: number;
}

export interface NewsItem {
  id: string;
  title: string;
  summary: string;
  source: string;
  timestamp: string;
  url: string;
  tickers: string[];
  sentiment: 'BULLISH' | 'BEARISH' | 'NEUTRAL';
  impact_score: number;
}

export interface OrderBookEntry {
  price: number;
  quantity: number;
  total: number;
}

export interface OrderBook {
  bids: OrderBookEntry[];
  asks: OrderBookEntry[];
}

export interface ApiCallLog {
  id: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  endpoint: string;
  status: number | 'ERR';
  latencyMs: number;
  responseSizeBytes: number;
  timestamp: string;
  requestBody?: unknown;
  responseBody?: unknown;
  error?: string;
}
