# Integration Blueprint

> **Classification**: Strategic Architecture Document
> **Project**: MONEYYYYYY — Indian AI Hedge Fund & Investment Research Platform
> **Status**: Approved for Planning

---

## 1. Executive Summary

This blueprint describes the migration path from MONEYYYYYY's current Sprint 12 architecture to an **Institutional-Grade AI Investment Operating System (IAIOS)** — a fully integrated platform combining:

- **OpenBB Open Data Platform** patterns for live financial data ingestion
- **TradingAgents** patterns for adversarial multi-agent investment committee deliberation
- **Paperclip** patterns for production-grade agent lifecycle management and operational reliability

The integration preserves and extends MONEYYYYYY's existing Clean Architecture, DDD, CQRS, Dependency Injection, Provider Abstraction, Testability, and Explainability principles without any refactoring of the existing domain model.

---

## 2. Current Architecture (Sprint 12 Baseline)

### 2.1 Layer Map

```
packages/
    domain/           <- Pure Python domain model (entities, value objects, events, policies)
        ai/           <- Prompt, ModelResponse, ReasoningTrace aggregate roots
        market/       <- MarketData, OHLCV, Ticker value objects
        portfolio/    <- Portfolio, Position, Trade aggregate roots
        brokerage/    <- BrokerAccount, Order, Fill aggregate roots
        research/     <- ResearchReport aggregate root
        backtesting/  <- Backtest aggregate root and equity curve

    application/      <- Use cases + port interfaces
        ports/
            market_data_port.py       <- MarketDataPort (abstract)
            llm_port.py               <- LLMPort (abstract)
            broker_port.py            <- BrokerPort (abstract)
            research_port.py          <- ResearchPort (abstract)
            storage_port.py           <- StoragePort (abstract)
            portfolio_port.py         <- PortfolioPort (abstract)
            notification_port.py      <- NotificationPort (abstract)

    infrastructure/   <- Concrete adapters wiring ports to external systems
        market_data/
            providers/
                mock_provider.py      <- Deterministic mock (ACTIVE)
                nse_provider.py       <- Placeholder skeleton
                yahoo_provider.py     <- Placeholder skeleton
        llm/
            providers/
                gemini/               <- Production (ACTIVE)
                claude/               <- Skeleton
                openai/               <- Skeleton
                deepseek/             <- Skeleton
                local/                <- Skeleton
            router.py                 <- LLMRouter with fallback
            registry.py               <- LLMProviderRegistry
            health.py                 <- ProviderHealthMonitor
            fallback.py               <- FallbackStrategy

    ai/               <- Multi-agent intelligence layer
        agents/
            fundamental_agent.py      <- ACTIVE
            technical_agent.py        <- ACTIVE
            news_agent.py             <- ACTIVE
            risk_agent.py             <- ACTIVE
            macro_agent.py            <- ACTIVE
        consensus/
            engine.py                 <- WeightedConsensusStrategy (ACTIVE)
            conflicts.py              <- ConflictDetector (ACTIVE)
            confidence.py             <- ConfidenceEngine (ACTIVE)
            weighting.py              <- WeightedVoting (ACTIVE)
            explanation.py            <- DecisionExplainer (ACTIVE)
            audit.py                  <- AuditRecorder (ACTIVE)
        prompts/
            registry.py               <- PromptRegistry (ACTIVE)
            composer.py               <- PromptComposer (ACTIVE)
            validator.py              <- PromptValidator (ACTIVE)
            token_budget.py           <- TokenBudgetManager (ACTIVE)
        memory/                       <- In-memory conversation store (ACTIVE)
        orchestrator/                 <- AgentOrchestrator (ACTIVE)
        evaluation/                   <- EvaluationEngine, BenchmarkRunner (ACTIVE)

    rag/              <- Retrieval-Augmented Generation foundation
        downloaders/  <- MockDocumentDownloader (ACTIVE)
        extractors/   <- PDFParser, HTMLParser, TableExtractor, SectionExtractor (ACTIVE)
        pipeline/     <- DocumentPipeline end-to-end ingestion (ACTIVE)
        chunking/     <- FixedSizeChunker, OverlappingChunker (ACTIVE)
        embeddings/   <- MockEmbeddingAdapter (ACTIVE)
        vector_store/ <- InMemoryVectorStoreAdapter (ACTIVE)
        metadata/     <- MetadataBuilder (ACTIVE)
        deduplication/-> DeduplicationEngine (ACTIVE)

    api/              <- FastAPI REST interface
```

### 2.2 Current State Assessment

| Capability | Status | Production Readiness |
|---|---|---|
| Domain model (equities, portfolio, brokerage) | Complete | Production |
| Clean Architecture layers | Complete | Production |
| LLM Multi-provider (Gemini live, others skeleton) | Partial | Gemini: Production |
| Market Data (mock only) | Partial | Development only |
| AI Agents (5 specialist agents) | Complete | Production |
| Consensus Engine | Complete | Production |
| Prompt Intelligence Framework | Complete | Production |
| AI Evaluation Framework | Complete | Production |
| RAG Foundation + Document Pipeline | Complete | Production |
| Live financial data | Missing | Not started |
| Adversarial debate | Missing | Not started |
| Agent lifecycle management | Partial | Development only |
| Indian F&O / Derivatives | Missing | Not started |
| Backtesting engine | Partial | Development only |

---

## 3. Target Architecture

```
INSTITUTIONAL-GRADE AI INVESTMENT OPERATING SYSTEM
===================================================

[Presentation Layer]
    FastAPI REST API        <- Existing
    WebSocket Streams       <- New (real-time portfolio updates)
    MCP Agent Interface     <- New (AI agent tool exposure)

[Application Layer]
    Portfolio Use Cases     <- Existing
    Research Use Cases      <- Existing
    Execution Use Cases     <- Existing + Extended
    NEW: AnalysisOrchestrationUseCase
    NEW: InvestmentCommitteeUseCase
    NEW: PortfolioRebalanceUseCase

[Port Interfaces — Application Layer]
    MarketDataPort          <- Extended (historical, quotes, corporate actions)
    FundamentalsPort        <- NEW (income statements, balance sheets, cash flows)
    NewsDataPort            <- NEW (company news, macro news)
    MacroDataPort           <- NEW (RBI policy, inflation, GDP, sector indicators)
    DerivativesPort         <- NEW (NSE F&O chain, options pricing)
    TechnicalIndicatorPort  <- NEW (RSI, MACD, Bollinger, VWAP)
    LLMPort                 <- Existing
    BrokerPort              <- Existing
    AgentSessionPort        <- NEW (lifecycle persistence)
    ToolExecutorPort        <- NEW (tool execution with retry/audit)

[AI Intelligence Layer — packages/ai/]
    InvestmentWorkflowOrchestrator <- NEW (Plan/Analyze/Debate/Decide/Reflect)
    AnalysisTaskQueue              <- NEW (priority-based dispatch)
    SessionCheckpoint              <- NEW (resumable sessions)

    Analyst Committee (6 agents):
        FundamentalAgent    <- Existing (extended)
        TechnicalAgent      <- Existing (extended)
        NewsAgent           <- Existing (extended)
        RiskAgent           <- Existing (extended)
        MacroAgent          <- Existing (extended)
        SentimentAgent      <- NEW (Indian market social sentiment)

    Debate Layer (NEW):
        BullResearcher      <- NEW (bull thesis generation)
        BearResearcher      <- NEW (bear thesis generation)
        BullBearDebateEngine <- NEW (configurable adversarial rounds)

    Consensus Layer (Existing + Extended):
        ConsensusEngine     <- Existing (extended with debate input)
        ConflictDetector    <- Existing
        ConfidenceEngine    <- Existing
        WeightedVoting      <- Existing
        DecisionExplainer   <- Existing
        AuditRecorder       <- Existing

    Decision Layer (NEW):
        TradeSignalExtractor <- NEW (BUY/SELL/HOLD with magnitude)
        DecisionReflector    <- NEW (post-hoc outcome feedback)

    Memory Layer (Extended):
        WorkingMemory        <- Extended
        SessionMemory        <- Extended
        LongTermMemory       <- NEW (financial-context filtered retrieval)

[Infrastructure Layer — packages/infrastructure/]
    Market Data Adapters:
        MockMarketDataAdapter          <- Existing (dev/test)
        OpenBBMarketDataAdapter        <- NEW (live historical + quotes)
        OpenBBFundamentalsAdapter      <- NEW
        OpenBBNewsAdapter              <- NEW
        OpenBBMacroAdapter             <- NEW
        OpenBBDerivativesAdapter       <- NEW (NSE F&O)
        NSEDirectAdapter               <- NEW (NSE bhav copy, indices)
        YahooFinanceAdapter            <- Existing (extended from skeleton)

    LLM Providers:
        GeminiAdapter                  <- Existing (production)
        ClaudeAdapter                  <- Existing (skeleton -> production)
        OpenAIAdapter                  <- Existing (skeleton)
        DeepSeekAdapter                <- Existing (skeleton)
        LocalLLMAdapter                <- Existing (skeleton)

    RAG + Document Pipeline:
        DocumentPipeline               <- Existing (extended)
        EmbeddingAdapter               <- NEW (Gemini Embeddings)
        VectorStoreAdapter             <- NEW (pgvector or Qdrant)

    Persistence:
        AgentSessionRepository         <- NEW (SQLAlchemy)
        ToolExecutionRepository        <- NEW (audit log)
        LongTermMemoryRepository       <- NEW

[Domain Layer — packages/domain/]
    <- ZERO CHANGES (no domain model modifications)
```

---

## 4. Migration Order

### Phase 0: Pre-conditions (Week 1)
- Complete documentation of current port interfaces
- Audit test coverage (target >90% on domain packages)
- Confirm all 256 tests pass cleanly
- Set up feature flag system (`FEATURE_FLAGS` in `AppSettings`)

### Phase 1: Data Foundation (Weeks 2-6)
Priority: Unblock AI agents from mock data

1. Define `FundamentalsPort`, `NewsDataPort`, `MacroDataPort` (interfaces only)
2. Implement `OpenBBMarketDataAdapter` behind `MarketDataPort`
3. Implement `OpenBBFundamentalsAdapter` behind `FundamentalsPort`
4. Implement `OpenBBNewsAdapter` behind `NewsDataPort`
5. Replace `MockMarketDataProvider` with feature-flag-controlled live adapter
6. Add NSE-specific normalization (INR currency, Indian date conventions)

### Phase 2: Agent Intelligence Enhancement (Weeks 7-12)
Priority: Institutional-grade multi-agent deliberation

1. Add `SentimentAgent` (Indian financial sentiment — Economic Times, Moneycontrol scraping)
2. Implement `BullResearcher` and `BearResearcher` components
3. Build `BullBearDebateEngine` with configurable `max_debate_rounds`
4. Extend `ConsensusEngine` to consume debate transcript as input
5. Add `TradeSignalExtractor` parsing final committee decision
6. Implement Dual-LLM routing strategy (`DEEP_THINK` vs `QUICK_THINK`)

### Phase 3: Production Reliability (Weeks 13-16)
Priority: Operationally production-grade

1. Design `InvestmentSessionState` state machine (lifecycle transitions)
2. Build `InvestmentWorkflowOrchestrator` (Plan/Analyze/Debate/Decide/Reflect)
3. Add `AnalysisTaskQueue` with priority dispatch
4. Implement `SessionCheckpoint` and resume logic
5. Extend `ToolExecutor` with timeout, retry, and audit logging
6. Implement financial-calendar-aware task scheduler
7. Add `AgentSessionRepository` for persistence

### Phase 4: Memory Intelligence (Weeks 17-19)
Priority: Cross-session learning and recall

1. Implement `WorkingMemory`, `SessionMemory`, `LongTermMemory` tiers
2. Add financial-context filtering to long-term retrieval
3. Implement `DecisionReflector` post-decision outcome feedback
4. Wire memory into agent prompts via `ContextBuilder`

### Phase 5: Derivatives and Advanced Data (Weeks 20-24)
Priority: Full Indian market coverage

1. Define `DerivativesPort` and `TechnicalIndicatorPort`
2. Implement `OpenBBDerivativesAdapter` for NSE F&O chain
3. Implement `NSEDirectAdapter` for real-time data
4. Add corporate actions pipeline (dividends, splits, buybacks, bonus)
5. Add MCX commodity data adapter

---

## 5. Affected Packages

| Package | Current State | Post-Integration State |
|---|---|---|
| `packages/application/ports/` | 7 ports | 12 ports (+5) |
| `packages/infrastructure/market_data/` | 1 mock + 2 skeletons | 6 live adapters |
| `packages/infrastructure/llm/` | 1 live + 4 skeletons | 2+ live providers |
| `packages/ai/agents/` | 5 agents | 8 agents (+3) |
| `packages/ai/consensus/` | 6 modules | 8 modules (+2 debate) |
| `packages/ai/orchestrator/` | 1 module | 4 modules (+workflow, queue, checkpoint) |
| `packages/ai/memory/` | 1 in-memory store | 3-tier memory system |
| `packages/ai/reasoning/` | 2 modules | 5 modules (+reflector, signal extractor) |
| `packages/rag/` | 10 submodules | 12 submodules (+embeddings, vector store) |
| `packages/domain/` | NO CHANGES | NO CHANGES |

---

## 6. Risk Assessment

### Risk 1: OpenBB Dependency Footprint (HIGH)
- **Risk**: `pip install openbb` installs 30+ transitive dependencies that may conflict with `google-generativeai`, `SQLAlchemy 2.x`, or `pydantic v2`.
- **Mitigation**: Install `openbb` in a separate optional dependency group. Use feature flags to isolate OpenBB import paths. Only load OpenBB adapters when `OPENBB_ENABLED=True`.
- **Rollback**: Disable feature flag → system falls back to `MockMarketDataProvider`.

### Risk 2: NSE Data Rate Limits (HIGH)
- **Risk**: NSE Public APIs have aggressive rate limits (60 requests/minute). Concurrent agent analysis sessions may exhaust quota.
- **Mitigation**: Implement `MarketDataCache` with TTL-based caching. Batch requests where possible. Add circuit breaker to prevent cascade failures.
- **Rollback**: Cache serves stale data with staleness warnings.

### Risk 3: LLM Cost Explosion During Debate Rounds (MEDIUM)
- **Risk**: `max_debate_rounds=10` with 8 agents could produce 80+ LLM calls per analysis session at significant cost.
- **Mitigation**: Default to `max_debate_rounds=3`. Use "quick" LLM model for debate, "deep" model only for final consensus. Add `TokenBudgetManager` hard limits per session.
- **Rollback**: Reduce `max_debate_rounds` to 1 via config without code changes.

### Risk 4: Agent State Persistence Complexity (MEDIUM)
- **Risk**: `InvestmentCommitteeSession` aggregate may grow large (many nested outputs) causing SQLAlchemy serialization complexity.
- **Mitigation**: Persist sessions as JSON blobs with schema versioning. Use event sourcing for session state rather than a relational model.
- **Rollback**: Fall back to in-memory sessions (lose resumability but maintain functionality).

### Risk 5: Indian Market Data Accuracy (MEDIUM)
- **Risk**: Yahoo Finance's India data has known gaps (incorrect dividend adjustments, missing corporate action events, timezone inconsistencies).
- **Mitigation**: Implement a data validation layer that cross-checks corporate actions against NSE official disclosures. Flag anomalies before they reach domain models.
- **Rollback**: Use mock data for affected tickers.

### Risk 6: Adversarial Debate Output Quality (LOW)
- **Risk**: Bull/Bear researchers may produce structurally identical arguments if the underlying LLM doesn't generate genuinely adversarial outputs.
- **Mitigation**: Use different LLM models for Bull vs. Bear researchers. Add system prompt constraints forcing genuinely contrarian positions. Evaluate with `EvaluationEngine`.
- **Rollback**: Disable debate, fall back to single-agent consensus.

---

## 7. Testing Strategy

### 7.1 Unit Testing
- Every new port interface requires at least one mock implementation and 5+ unit tests
- All new domain value objects tested in isolation with `pytest`
- All `mypy --strict` checks must pass before any PR merge

### 7.2 Integration Testing
- Add `tests/integration/` directory for end-to-end session tests with mocked external APIs
- `DocumentPipeline` integration tests against sample annual reports
- `InvestmentWorkflowOrchestrator` integration tests with mock agent responses

### 7.3 Performance Testing
- Benchmark `LLMRouter` latency with all 5 providers configured
- Benchmark `MarketDataRouter` with caching enabled vs. disabled
- Profile `BullBearDebateEngine` memory usage at 10 debate rounds

### 7.4 Regression Testing
- Every new adapter must have a dedicated regression test with recorded (cassette) API responses
- `EvaluationEngine` benchmark datasets updated with new agent configurations

---

## 8. Rollback Strategy

| Component | Rollback Mechanism |
|---|---|
| OpenBB adapters | `OPENBB_ENABLED=False` → `MockMarketDataProvider` |
| Live LLM providers | `LLM_PROVIDER=gemini-mock` → `MockLLMAdapter` |
| Debate engine | `MAX_DEBATE_ROUNDS=0` → skip debate phase |
| Session persistence | `SESSION_PERSISTENCE=memory` → `InMemorySessionStore` |
| Vector store | `VECTOR_STORE=memory` → `InMemoryVectorStoreAdapter` |
| Document ingestion | `INGESTION_MODE=mock` → `MockDocumentDownloader` |

All rollback switches are configuration-level changes with no code deploys required.
