# Implementation Roadmap

> **Classification**: Strategic Engineering Roadmap
> **Project**: MONEYYYYYY — Institutional AI Investment Operating System
> **Horizon**: 12 Milestones across approximately 36-48 engineering weeks

---

## Roadmap Philosophy

Each milestone delivers a **complete, independently deployable vertical slice** of functionality. No milestone leaves the system in a broken or partially functional state. Tests must pass at 100% before the next milestone begins.

**Quality gates per milestone:**
- `black --check .` passes
- `ruff check .` passes
- `mypy packages/` passes (no type errors)
- `pytest` passes (100% of tests)
- New feature covered by unit + integration tests
- Architecture review confirms Clean Architecture compliance

---

## Milestone 1 — OpenBB Data Layer

> **Objective**: Replace mock market data with production-grade live financial data
> **Duration**: 4-6 weeks
> **Primary Reference**: OpenBB Architecture Analysis (OPENBB_ANALYSIS.md)

### Sprint 1.1 — Port Extensions (1 week)
**Deliverables:**
- `FundamentalsPort` (abstract) — income_statement, balance_sheet, cash_flow, key_metrics
- `NewsDataPort` (abstract) — company_news, sector_news, earnings_alerts
- `MacroDataPort` (abstract) — rbi_rates, inflation_cpi, gdp_growth, sector_pmi
- `CorporateActionsPort` (abstract) — dividends, splits, buybacks, bonus_issues, rights

**Testing:**
- Mock implementations for each new port
- 10+ unit tests per port interface

### Sprint 1.2 — OpenBB Market Data Adapter (1-2 weeks)
**Deliverables:**
- `OpenBBMarketDataAdapter(MarketDataProvider)` implementing:
  - `get_historical_ohlcv(ticker, from_date, to_date)`
  - `get_current_quote(ticker)`
  - `get_company_profile(ticker)`
  - `get_market_status(exchange)`
- `OPENBB_ENABLED` feature flag in `AppSettings`
- NSE ticker normalization (RELIANCE -> RELIANCE.NS)
- Currency conversion: OpenBB USD-denominated fields -> INR using `Decimal`

**Testing:**
- Cassette-recorded integration tests (no live network calls in CI)
- Schema validation tests (all monetary fields use `Decimal`, never `float`)

### Sprint 1.3 — Fundamentals and News Adapters (1-2 weeks)
**Deliverables:**
- `OpenBBFundamentalsAdapter(FundamentalsPort)`:
  - `get_income_statement(ticker, period="annual")`
  - `get_balance_sheet(ticker, period="annual")`
  - `get_cash_flow_statement(ticker, period="annual")`
  - `get_key_ratios(ticker)` — P/E, P/B, EV/EBITDA, ROCE, ROE
- `OpenBBNewsAdapter(NewsDataPort)`:
  - `get_company_news(ticker, limit=50)`
  - `get_sector_news(sector, limit=20)`
- `MarketDataRouter` — multi-provider routing with `LLMRouter` pattern

**Testing:**
- Normalization tests verifying all financial ratios are within plausible Indian market ranges
- Provider fallback tests confirming graceful degradation

### Sprint 1.4 — Corporate Actions and NSE Direct (1 week)
**Deliverables:**
- `OpenBBCorporateActionsAdapter(CorporateActionsPort)`:
  - Dividend history, stock splits, bonus issues
- `NSEBhavCopyAdapter` — direct NSE end-of-day bhav copy parser
- SEBI filing metadata enrichment in document pipeline
- Indian market calendar (NSE/BSE trading days, holidays)

**Benefits:** Agents can analyze actual financial statements rather than mock data
**Tradeoffs:** OpenBB dependency footprint; Yahoo Finance data quality issues for Indian tickers
**Risks:** NSE rate limits; currency conversion precision
**Compatibility:** Zero domain layer changes; all new adapters are behind existing ports
**Long-term Maintainability:** Provider-agnostic ports allow replacing OpenBB with Bloomberg or Refinitiv in future without touching agent code

---

## Milestone 2 — TradingAgents Planner

> **Objective**: Upgrade agent analysis from independent outputs to structured deliberation
> **Duration**: 4-5 weeks
> **Primary Reference**: TradingAgents Architecture Analysis (TRADING_AGENTS_ANALYSIS.md)

### Sprint 2.1 — Sentiment Agent (1 week)
**Deliverables:**
- `SentimentAgent(BaseAgent)` using Indian financial sentiment sources:
  - Economic Times news feed
  - Moneycontrol corporate announcements
  - NSE bulk and block deal data
  - FII/DII daily flow data
- Prompt templates in `packages/ai/prompts/templates/sentiment/`

### Sprint 2.2 — Bull/Bear Researcher Framework (1-2 weeks)
**Deliverables:**
- `BullResearcher(BaseAgent)` — generates bullish investment thesis from analyst output
- `BearResearcher(BaseAgent)` — generates contrarian bearish thesis
- `DebateRound` domain entity tracking each round of Bull/Bear exchange
- `BullBearDebateEngine`:
  - `conduct_debate(analyst_outputs, max_rounds=3) -> DebateTranscript`
  - Configurable exit conditions (agreement threshold, max_rounds)
  - Token budget enforcement per round

**Testing:**
- Debate quality tests verifying bull/bear positions are genuinely contrarian
- Token budget enforcement tests

### Sprint 2.3 — Extended Consensus Engine (1 week)
**Deliverables:**
- `ConsensusEngine` extended to accept `DebateTranscript` as additional input
- `DebateTranscript` influences final agent weights:
  - Strong bull argument -> increase `FundamentalAgent` weight
  - Risk concerns raised -> increase `RiskAgent` weight
- `TradeSignalExtractor`:
  - Parses final consensus into `TradeSignal(action=BUY/SELL/HOLD, conviction=HIGH/MEDIUM/LOW, suggested_size_pct=Decimal)`

### Sprint 2.4 — Dual LLM Routing Strategy (1 week)
**Deliverables:**
- `RoutingStrategy` enum: `DEEP_THINK`, `QUICK_THINK`, `COST_OPTIMIZED`
- `LLMRouter.route(task_complexity: RoutingStrategy) -> LLMPort`
- Strategy mapping:
  - Analyst analysis, debate, final consensus -> `DEEP_THINK` (Gemini Pro / Claude Sonnet)
  - Signal extraction, state routing, memory summarization -> `QUICK_THINK` (Gemini Flash)
  - Batch background processing -> `COST_OPTIMIZED` (DeepSeek / Local)

**Benefits:** Adversarial debate produces richer, more auditable investment theses; Dual-LLM cuts costs 40-60%
**Tradeoffs:** Debate adds 2-5x latency vs. single-agent analysis
**Risks:** LLM may produce structurally identical bull/bear arguments; added cost
**Compatibility:** ConsensusEngine fully backward-compatible; debate output is additional input, not replacement
**Long-term Maintainability:** Debate depth configurable at runtime; no code changes needed to tune

---

## Milestone 3 — Paperclip Runtime

> **Objective**: Production-grade agent lifecycle management, retry, and observability
> **Duration**: 4-5 weeks
> **Primary Reference**: Paperclip Architecture Analysis (PAPERCLIP_ANALYSIS.md)

### Sprint 3.1 — Investment Session Lifecycle (1-2 weeks)
**Deliverables:**
- `InvestmentSessionState` enum:
  `CREATED -> PLANNING -> ANALYZING -> DEBATING -> DECIDING -> REFLECTING -> COMPLETED`
  and `ERROR -> RETRYING -> FAILED`
- `InvestmentCommitteeSession` aggregate root in `packages/domain/ai/`
- `AgentSessionPort` (abstract)
- `AgentSessionRepository` (SQLAlchemy implementation)
- Session state persistence with event sourcing

### Sprint 3.2 — Tool Execution Framework (1 week)
**Deliverables:**
- `ToolExecutor(ToolExecutorPort)`:
  - Configurable timeout per tool category (market data: 5s, LLM: 60s, fundamentals: 10s)
  - Exponential backoff retry (3 attempts, 2^n seconds)
  - Tool input/output logging as `ToolExecutionRecord`
  - Tool output schema validation (domain invariant checks)
- `ToolExecutionRepository` for audit log persistence

### Sprint 3.3 — Analysis Task Queue (1 week)
**Deliverables:**
- `AnalysisTaskQueue`:
  - Priority levels: `CRITICAL > HIGH > NORMAL > LOW`
  - `CRITICAL`: Intraday risk alerts, stop-loss triggers
  - `HIGH`: Pre-market session analysis
  - `NORMAL`: Routine research sessions
  - `LOW`: Background batch processing
- Financial-calendar-aware scheduler (respects NSE/BSE trading hours and holidays)
- Rate limiting per external data provider

### Sprint 3.4 — Session Checkpoint and Resume (1 week)
**Deliverables:**
- `SessionCheckpoint` persisting intermediate agent outputs
- Resume from last checkpoint on timeout or failure
- `InvestmentWorkflowOrchestrator`:
  - Full `PLANNING -> ANALYZING -> DEBATING -> DECIDING -> REFLECTING` lifecycle
  - Rollback to last good checkpoint on any phase failure

**Benefits:** Sessions survive LLM timeouts; full audit trail; operator visibility into running analyses
**Tradeoffs:** Persistence overhead; session state can become complex
**Risks:** SQLAlchemy serialization of large nested objects; checkpoint bloat
**Compatibility:** All existing tests continue passing; session management is additive
**Long-term Maintainability:** Event-sourced state provides full audit trail for SEBI compliance

---

## Milestone 4 — Investment Committee

> **Objective**: Full multi-agent investment committee as a production-grade feature
> **Duration**: 3-4 weeks

**Deliverables:**
- `InvestmentCommitteeUseCase`:
  - Accepts: `ticker`, `analysis_date`, `investment_mandate`, `risk_tolerance`
  - Executes: Full 6-agent analysis + debate + consensus
  - Returns: `InvestmentCommitteeDecision` with full audit trail
- `InvestmentCommitteeDecision` domain entity:
  - `trade_signal: TradeSignal`
  - `debate_transcript: DebateTranscript`
  - `agent_outputs: dict[AgentType, AgentResult]`
  - `consensus_decision: ConsensusIntelligenceDecision`
  - `confidence_score: Percentage`
  - `reasoning_trace: ReasoningTrace`
  - `audit_hash: str` (SHA-256 for immutability verification)
- FastAPI endpoint: `POST /api/v1/committee/analyze`
- Async execution with `InvestmentSessionState` streaming via WebSocket

**Benefits:** First fully production-grade end-to-end investment analysis feature
**Tradeoffs:** 15-30 minute analysis sessions for thorough debate
**Risks:** LLM cost per session; concurrent session management complexity
**Compatibility:** Zero domain model changes; new use case + endpoint only

---

## Milestone 5 — Portfolio Intelligence

> **Objective**: AI-driven portfolio construction and rebalancing recommendations
> **Duration**: 3-4 weeks

**Deliverables:**
- `PortfolioIntelligenceAgent` — analyses portfolio composition vs. market conditions
- `PortfolioRebalanceUseCase`:
  - Accepts: current holdings, target allocations, risk mandate
  - Executes: AI-driven rebalancing analysis
  - Returns: Ranked rebalancing recommendations with rationale
- Position sizing: Kelly Criterion implementation with `Decimal` precision
- Portfolio risk attribution: VaR, CVaR, Sharpe, Sortino, Max Drawdown
- SEBI mandate compliance checking (sector concentration limits, single-stock limits)
- `PortfolioRiskReport` aggregate with explainable outputs

---

## Milestone 6 — Execution Intelligence

> **Objective**: AI-assisted order execution with market impact minimization
> **Duration**: 3-4 weeks

**Deliverables:**
- `ExecutionAgent` — optimizes trade timing and order splitting
- TWAP/VWAP execution strategy implementation
- Market impact estimation using historical intraday volume profiles
- `ExecutionAlgorithmPort` (abstract) with `TWAPAdapter`, `VWAPAdapter`
- Broker integration via existing `BrokerPort`:
  - Zerodha Kite adapter
  - Dhan adapter
- Pre-trade risk checks (exposure limits, position limits, daily loss limits)
- Post-trade reporting and reconciliation

---

## Milestone 7 — Futures and Options Intelligence

> **Objective**: Full NSE F&O analysis capability
> **Duration**: 5-6 weeks

**Deliverables:**
- `DerivativesPort` full implementation:
  - NSE F&O chain retrieval (all strikes, all expiries)
  - Implied volatility surface construction
  - Put/Call ratio calculation
  - Options Greeks: Delta, Gamma, Theta, Vega
- `OptionsAnalysisAgent`:
  - Identifies unusual options activity (institutional positioning signals)
  - Generates hedging recommendations for portfolio positions
  - Detects covered call, protective put, iron condor opportunities
- `FuturesAnalysisAgent`:
  - Tracks futures premium/discount to spot (basis)
  - Rollover cost analysis
  - FII futures positioning (long/short ratio)
- PCR (Put/Call Ratio) as macro sentiment indicator in `MacroAgent`

---

## Milestone 8 — MCX Commodity Intelligence

> **Objective**: Multi-commodity exchange data, analysis, and trading support
> **Duration**: 3-4 weeks

**Deliverables:**
- `MCXDataPort` (abstract) — commodity price, open interest, delivery data
- `MCXAdapter` implementing `MCXDataPort`:
  - Gold, Silver, Crude Oil, Natural Gas, Copper, Zinc prices
  - MCX commodity options chain
  - Delivery-based settlement data
- `CommodityAgent`:
  - Macro commodity analysis (OPEC, RBI forex impact, USD-INR on crude)
  - Gold-equity correlation analysis
  - Commodity hedging recommendations for portfolio exposure
- MCX historical data via `DocumentPipeline` (MCX bhav copy ingestion)
- Commodity price impact analysis on equity sectors (Crude -> Paints, Aviation, OMCs)

---

## Milestone 9 — RAG-Enhanced Research

> **Objective**: Ground agent analysis in ingested financial documents
> **Duration**: 3-4 weeks

**Deliverables:**
- Production embedding adapter (`GeminiEmbeddingAdapter` replacing `MockEmbeddingAdapter`)
- Production vector store (`pgvector` or `Qdrant` replacing `InMemoryVectorStoreAdapter`)
- Annual report automatic ingestion workflow (triggered by NSE filing alert)
- `RAGContextBuilder` enriching agent prompts with relevant document chunks
- Earnings call transcript parser (speaker diarization, Q&A extraction)
- Management commentary NLP (bullish/bearish language detection)
- SEBI filing metadata extraction (related-party transactions, pledge data)

---

## Milestone 10 — Backtesting and Strategy Validation

> **Objective**: Quantitative strategy backtesting with AI-generated signals
> **Duration**: 4-5 weeks

**Deliverables:**
- Historical data pipeline (10+ years NSE OHLCV via `OpenBBMarketDataAdapter`)
- `BacktestEngine` complete implementation:
  - Event-driven backtesting (no look-ahead bias by design)
  - Indian market microstructure: STT, brokerage, impact cost, settlement
  - Corporate action adjustment (dividend reinvestment, split normalization)
- AI signal backtesting: evaluate `InvestmentCommitteeDecision` historical accuracy
- Strategy metrics: Sharpe, Sortino, Calmar, Max Drawdown, CAGR, Alpha, Beta
- `EvaluationEngine` integration: measure agent prediction accuracy historically
- Walk-forward optimization for strategy parameters

---

## Milestone 11 — Observability and Operations

> **Objective**: Production monitoring, alerting, and operational excellence
> **Duration**: 2-3 weeks

**Deliverables:**
- Structured logging for every AI agent call, LLM invocation, and tool execution
- OpenTelemetry traces for full request lifecycle (ingest -> analyze -> decide -> execute)
- Prometheus metrics: LLM latency, token cost, agent confidence distribution
- Grafana dashboards: AI portfolio performance, agent consensus quality
- Alerting: LLM cost thresholds, market data staleness, risk limit breaches
- Runbook documentation for all operational scenarios

---

## Milestone 12 — Institutional Compliance and Audit

> **Objective**: Full institutional-grade compliance and audit readiness
> **Duration**: 3-4 weeks

**Deliverables:**
- `ComplianceEngine`:
  - SEBI Regulation 30 compliance checking
  - Insider trading window detection
  - Related-party transaction flagging
  - Concentration limit enforcement
- Complete audit trail for every investment decision (SHA-256 signed)
- Regulatory report generation (SEBI, NSE, MCA filings)
- GDPR/PDPA-compliant data handling for any PII in research documents
- SOC 2 compliance documentation for all data storage and access patterns
- Independent decision audit: all AI recommendations reviewable by human portfolio manager before execution

---

## Consolidated Effort Estimate

| Milestone | Focus | Duration | Complexity |
|---|---|---|---|
| M1 — OpenBB Data Layer | Live financial data | 4-6 weeks | High |
| M2 — TradingAgents Planner | Adversarial debate | 4-5 weeks | Very High |
| M3 — Paperclip Runtime | Operational reliability | 4-5 weeks | High |
| M4 — Investment Committee | End-to-end use case | 3-4 weeks | Very High |
| M5 — Portfolio Intelligence | Portfolio AI | 3-4 weeks | High |
| M6 — Execution Intelligence | Order execution | 3-4 weeks | High |
| M7 — F&O Intelligence | Derivatives | 5-6 weeks | Very High |
| M8 — MCX Commodities | Commodities | 3-4 weeks | High |
| M9 — RAG-Enhanced Research | Document grounding | 3-4 weeks | High |
| M10 — Backtesting | Strategy validation | 4-5 weeks | Very High |
| M11 — Observability | Operations | 2-3 weeks | Medium |
| M12 — Compliance and Audit | Institutional governance | 3-4 weeks | High |
| **Total** | | **41-54 weeks** | |

---

## Architecture Invariants (Must Never Be Violated)

Across all 12 milestones, the following principles are non-negotiable:

1. **Domain Layer Purity**: `packages/domain/` must remain zero-dependency (no OpenBB, LangGraph, or any third-party library imports).

2. **Port-Driven Integration**: Every new external dependency must be wrapped behind an abstract port in `packages/application/ports/`. No application or AI layer code may directly import from infrastructure.

3. **Decimal Monetary Precision**: No `float` for any monetary value. All prices, quantities, P&L calculations use `decimal.Decimal`.

4. **Complete Type Safety**: Every new module ships with complete `mypy --strict` compliance. No implicit `Any`.

5. **100% Test Gate**: No milestone closes until `pytest` passes 100% across all tests.

6. **Auditability**: Every investment decision carries an immutable, SHA-256 signed audit record. No decision is taken without a traceable reasoning chain.

7. **Testable Without Live APIs**: Every component has a mock adapter. The full test suite runs without any network calls. Live adapters are integration-tested separately.

8. **No Hardcoded Secrets**: All API keys, credentials, and connection strings must be loaded from environment variables via `AppSettings`.

9. **Feature Flag Rollback**: Every new live data adapter or agent feature must be controllable via environment variable feature flags without code deployment.

10. **Clean Architecture Layering**: UI/API -> Application (Use Cases + Ports) -> Infrastructure (Adapters) -> Domain. No reverse dependencies. No skipping layers.
