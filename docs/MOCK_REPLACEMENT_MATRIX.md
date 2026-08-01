# Mock Replacement Matrix & System-Wide Integration Audit

> **Document Version**: 1.0.0  
> **Status**: APPROVED ARCHITECTURE AUDIT  
> **Target Release**: ALPHA MOCK-REPLACEMENT MILESTONE  
> **Scope**: Complete Codebase Analysis (`packages/`, `frontend/`, `tests/`, `docs/`, Infrastructure, DI, LLM, RAG, OpenBB, Market Data, Committee)

---

## Executive Audit Summary

This document provides an absolute, end-to-end audit of all endpoints, application services, domain models, infrastructure providers, and UI layers within the **MONEYYYYYY** platform repository. The objective is to provide a zero-ambiguity blueprint for replacing every remaining synthetic payload, hardcoded default, and unwired infrastructure adapter with live production pipelines.

---

## 1. Complete API Endpoint Mock Replacement Matrix

| Endpoint | Method | Router File | Application Service | Use Case | Domain Service | Infra Provider | Current Data Source | Current Provider | Response Type | Mock? | Hardcoded? | Synthetic? | Cached? | Live? | Target Production Provider | Priority | Risk Level |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- | :---: | :---: |
| `GET /health` | GET | `health.py` | N/A | N/A | HealthCheck | Container | Memory | Container DI | `HealthResponse` | No | No | No | No | Yes | Health Diagnostics | P2 | Low |
| `GET /version` | GET | `health.py` | N/A | N/A | VersionInfo | AppSettings | AppSettings | AppSettings | `VersionResponse` | No | No | No | No | Yes | Infrastructure Config | P2 | Low |
| `GET /market/{ticker}` | GET | `market.py` | `CompanyDataRetrievalService` | `AnalyzeStockUseCase` | QuoteService | `ProviderManager` | Multi-Provider Engine | OpenBB / Yahoo / NSE | `MarketQuoteResponse` | No | No | No | Yes | Yes | OpenBB Platform / Yahoo / NSE | P0 | Low |
| `GET /company-intelligence/{ticker}` | GET | `company_intelligence.py` | `CompanyDataRetrievalService` | N/A | Financial/Technical/Macro Services | Service Helpers | Hardcoded Dict Fallbacks | Mock Adapters | `CompanyIntelligenceResponse` | Yes | Yes | Yes | No | Partial | OpenBB SDK + RAG Pipeline | P0 | High |
| `POST /analyze` | POST | `analyze.py` | `ResearchApplicationService` | `AnalyzeStockUseCase` | `PortfolioPolicy` | `MockResearchAdapter` | In-Memory Mock | `MockResearchAdapter` | `AnalyzeStockResultDTO` | Yes | Yes | Yes | No | No | LLM Committee + OpenBB | P0 | High |
| `POST /committee/evaluate` | POST | `committee.py` | `CompanyAgentCoordinatorService` | N/A | `ConsensusEngine` | `MockLLMAdapter` | Static Multi-Agent Rules | `MockLLMAdapter` | `CommitteeEvaluateResponse` | Yes | Yes | Yes | No | No | Intelligent Committee Orchestrator | P0 | High |
| `POST /auth/signup` | POST | `auth.py` | `AuthApplicationService` | N/A | UserDomain | `SQLUserRepository` | SQLite / PostgreSQL | `SQLUserRepository` | `TokenResponse` | No | No | No | No | Yes | Production DB (PostgreSQL) | P1 | Low |
| `POST /auth/login` | POST | `auth.py` | `AuthApplicationService` | N/A | UserDomain | `SQLUserRepository` | SQLite / PostgreSQL | `SQLUserRepository` | `TokenResponse` | No | No | No | No | Yes | Production DB (PostgreSQL) | P1 | Low |
| `POST /auth/refresh` | POST | `auth.py` | `AuthApplicationService` | N/A | UserDomain | Security JWT | Security JWT | Security JWT | `TokenResponse` | No | No | No | No | Yes | Production Auth Service | P1 | Low |
| `GET /user/profile` | GET | `user.py` | `AuthApplicationService` | N/A | UserDomain | `SQLUserRepository` | SQLite / PostgreSQL | `SQLUserRepository` | `UserProfileResponse` | No | No | No | No | Yes | Production DB (PostgreSQL) | P1 | Low |
| `PUT /user/profile` | PUT | `user.py` | `AuthApplicationService` | N/A | UserDomain | `SQLUserRepository` | SQLite / PostgreSQL | `SQLUserRepository` | `UserProfileResponse` | No | No | No | No | Yes | Production DB (PostgreSQL) | P1 | Low |

---

## 2. Comprehensive Endpoint Execution & Dependency Chains

### Execution Trace: `GET /market/{ticker}`
```
GET /market/{ticker} [packages/api/routers/market.py]
 └── Depends(get_provider_manager) [packages/api/dependencies.py]
      └── ProviderManager.get_quote(ticker) [packages/infrastructure/market_data/provider_manager.py]
           ├── MarketDataCache.get_quote(ticker) [packages/infrastructure/market_data/cache.py] (Cache Hit -> Return)
           ├── OpenBBMarketDataProvider.get_quote(ticker) [packages/infrastructure/market_data/providers/openbb_provider.py]
           ├── YahooMarketDataProvider.get_quote(ticker) [packages/infrastructure/market_data/providers/yahoo_provider.py] (Fallback)
           └── NSEMarketDataProvider.get_quote(ticker) [packages/infrastructure/market_data/providers/nse_provider.py] (Fallback)
```

### Execution Trace: `GET /company-intelligence/{ticker}`
```
GET /company-intelligence/{ticker} [packages/api/routers/company_intelligence.py]
 └── CompanyIntelligenceOrchestrator.analyze_company() [packages/application/company_intelligence/orchestrator.py]
      ├── CompanyDataRetrievalService.retrieve_market_snapshot() [packages/application/company_intelligence/services.py]
      ├── CompanyDataRetrievalService.retrieve_financial_highlights() [packages/application/company_intelligence/services.py] (Hardcoded Fallbacks)
      ├── CompanyDataRetrievalService.retrieve_technical_analysis() [packages/application/company_intelligence/services.py] (Hardcoded ₹2500)
      ├── CompanyDataRetrievalService.retrieve_news_section() [packages/application/company_intelligence/services.py]
      ├── CompanyDataRetrievalService.retrieve_corporate_actions() [packages/application/company_intelligence/services.py]
      ├── CompanyDataRetrievalService.retrieve_macro_context() [packages/application/company_intelligence/services.py] (Hardcoded 6.50% Repo)
      ├── CompanyDocumentService.discover_and_retrieve_rag_evidence() [packages/application/company_intelligence/services.py] (Synthetic Chunks)
      └── CompanyAgentCoordinatorService.evaluate_committee() [packages/application/company_intelligence/services.py] (Mock Agent Outputs)
```

---

## 3. Discovered Mock Values, Hardcoded Constants & Synthetic Payloads

1. **Hardcoded Financial Quantities & Technical Closings**:
   - `packages/application/company_intelligence/services.py`:
     - Line 128: Net Income fallback `25000000.00`
     - Line 129: Total Assets fallback `500000000.00`
     - Line 131: Total Liabilities fallback `200000000.00`
     - Line 134: Operating Cash Flow fallback `30000000.00`
     - Line 136: Free Cash Flow fallback `20000000.00`
     - Line 150: Last close price fallback `Decimal("2500.00")`
   - `packages/infrastructure/market_data/providers/openbb_provider.py`:
     - Line 67: Base quote price `"2500.00"`
     - Line 93: Base historical bar price `Decimal("2500.00")`
     - Line 167: Income statement total revenue `"100000000.00"`
     - Line 186: Balance sheet total assets `"500000000.00"`
     - Line 204: Cash flow statement operating cash flow `"30000000.00"`
     - Line 244: Repo rate `"6.50"`
   - `packages/infrastructure/openbb/services.py`:
     - Line 49: Quote price `"2500.00"`
     - Line 92: Historical OHLCV base price `Decimal("2500.00")`

2. **Synthetic RAG Chunks**:
   - `packages/application/company_intelligence/services.py` (Lines 267-280): Synthetic chunk text `"Annual Report FY25 for ... Revenue grew 18.5% YoY..."` with hardcoded page numbers and document IDs.

3. **Hardcoded Recommendation Scores & Consensus Decisions**:
   - `packages/application/use_cases/analyze_stock_use_case.py` (Line 86): Default fallback score `Decimal("0.75")` / `RecommendationType.BUY`.
   - `packages/infrastructure/adapters/mock_research_adapter.py` (Line 46): Hardcoded score `Decimal("0.80")` / `ConfidenceScore(Decimal("0.85"))`.

---

## 4. OpenBB Capabilities Integration Matrix

| Capability | Status | File Location | Operational Notes |
| :--- | :--- | :--- | :--- |
| **Quotes** | Implemented | `packages/infrastructure/market_data/provider_manager.py` | Multi-tier failover live. |
| **Historical OHLCV** | Partially Implemented | `packages/infrastructure/market_data/providers/openbb_provider.py` | Return synthetic bar calculations. |
| **Fundamentals** | Not Wired | `packages/infrastructure/market_data/services/fundamental_service.py` | Delegates to static dictionary provider methods. |
| **Balance Sheet** | Not Wired | `packages/infrastructure/openbb/adapter.py` | Needs live OpenBB platform SDK binding. |
| **Income Statement** | Not Wired | `packages/infrastructure/openbb/adapter.py` | Needs live OpenBB platform SDK binding. |
| **Cash Flow** | Not Wired | `packages/infrastructure/openbb/adapter.py` | Needs live OpenBB platform SDK binding. |
| **ETF Info** | Not Wired | `packages/infrastructure/market_data/services/etf_service.py` | Provider returning static placeholder data. |
| **News** | Partially Implemented | `packages/infrastructure/market_data/services/news_service.py` | Synthetic sentiment score `0.85`. |
| **Macro Data** | Partially Implemented | `packages/infrastructure/market_data/services/macro_service.py` | Hardcoded repo rate `6.50%`. |
| **Corporate Actions**| Partially Implemented | `packages/infrastructure/market_data/services/corporate_service.py` | Static dividend event generation. |
| **Economic Calendar**| Partially Implemented | `packages/infrastructure/market_data/services/economic_calendar_service.py` | Static event generation. |
| **Sector Perf** | Not Wired | `packages/infrastructure/market_data/services/sector_service.py` | Static sector performance map. |
| **Options** | Unused | `packages/infrastructure/openbb/adapter.py` | Domain/Infra types missing options chain models. |
| **Futures** | Unused | `packages/infrastructure/openbb/adapter.py` | Domain types missing futures models. |
| **Currencies** | Unused | `packages/infrastructure/market_data/normalizers/currency.py` | Static symbol converter. |
| **Commodities** | Unused | N/A | Unimplemented. |
| **Indices** | Unused | N/A | Unimplemented. |

---

## 5. Multi-Provider LLM Infrastructure Audit

| Adapter Name | File Location | Configured? | Injected in DI? | Production Readiness |
| :--- | :--- | :---: | :---: | :--- |
| **`GeminiAdapter`** | `packages/infrastructure/llm/gemini_adapter.py` | Yes | Yes (Prod Mode) | **Production-Ready** (Google GenAI SDK) |
| **`ClaudeAdapter`** | `packages/infrastructure/llm/providers/claude/adapter.py` | Yes | No | Skeleton Adapter |
| **`OpenAIAdapter`** | `packages/infrastructure/llm/providers/openai/adapter.py` | Yes | No | Skeleton Adapter |
| **`DeepSeekAdapter`**| `packages/infrastructure/llm/providers/deepseek/adapter.py` | Yes | No | Skeleton Adapter |
| **`LocalLLMAdapter`**| `packages/infrastructure/llm/providers/local/adapter.py` | Yes | No | Local Ollama/vLLM Skeleton |
| **`MockLLMAdapter`** | `packages/infrastructure/adapters/mock_llm_adapter.py` | Yes | Yes (Dev Mode) | **In-Memory Mock** |

---

## 6. Frontend Audit (React / Vite Console)

| Component / Page | Location | Data Source | API Endpoint Consumed | Loading State? | Error State? | Audit Status |
| :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| **`LiveMarketPage`** | `frontend/src/pages/LiveMarketPage.tsx` | Real API | `GET /market/{ticker}` | Yes | Yes | **Production Ready** |
| **`CompanyAnalysisPage`**| `frontend/src/pages/CompanyAnalysisPage.tsx` | Partial API | `GET /company-intelligence/{ticker}` | Yes | Yes | Consumes hardcoded backend data |
| **`CommitteePage`** | `frontend/src/pages/CommitteePage.tsx` | Partial API | `POST /committee/evaluate` | Yes | Yes | Consumes mock LLM agent results |
| **`SystemHealthPage`** | `frontend/src/pages/SystemHealthPage.tsx` | Real API | `GET /health`, `GET /version` | Yes | Yes | **Production Ready** |
| **`ApiExplorerPage`** | `frontend/src/pages/ApiExplorerPage.tsx` | Real API | All System Endpoints | Yes | Yes | **Production Ready** |
| **`DashboardPage`** | `frontend/src/pages/DashboardPage.tsx` | Mock API | Composite Frontend Calls | Yes | Yes | Requires live telemetry wiring |

---

## 7. Unwired Infrastructure & Dead Code Audit

1. **`IntelligentInvestmentCommittee` Orchestrator**:
   - Location: `packages/ai/committee/orchestrator.py`
   - Description: Full 8-component committee architecture (Planner, Critic, Judge, TaskGraph, Scheduler, Memory) is completely implemented and tested in unit tests, but `CompanyAgentCoordinatorService` in `packages/application/company_intelligence/services.py` still invokes individual agent stubs directly.
2. **RAG Vector Retriever & Document Pipeline**:
   - Location: `packages/rag/pipeline/document_pipeline.py`, `packages/rag/retriever/vector_retriever.py`
   - Description: End-to-end chunking, embedding, vector store indexing, and re-ranking pipeline is built, but `CompanyDocumentService` in `packages/application/company_intelligence/services.py` bypasses it to construct hardcoded synthetic evidence chunks.
3. **OpenBB Secondary Infrastructure Services**:
   - Location: `packages/infrastructure/market_data/services/` (`fundamental_service.py`, `corporate_service.py`, `macro_service.py`, etc.)
   - Description: Service wrappers exist but delegate to `OpenBBMarketDataProvider` mock methods.
