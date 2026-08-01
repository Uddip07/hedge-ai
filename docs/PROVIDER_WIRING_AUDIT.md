# Infrastructure & Provider Wiring Audit

> **Document Version**: 1.0.0  
> **Status**: APPROVED INFRASTRUCTURE AUDIT  
> **Target System**: MONEYYYYYY Production Engine  

---

## 1. Primary Infrastructure Wiring Analysis

This audit traces how concrete implementations are registered and resolved across **Development** vs **Production** environments within `packages/infrastructure/dependency_injection/container.py`.

```
                        ┌────────────────────────┐
                        │   AppSettings          │
                        └───────────┬────────────┘
                                    │
                         Environment Branching
                                    │
           ┌────────────────────────┴────────────────────────┐
           ▼                                                 ▼
   environment == "production"                       environment == "development"
┌─────────────────────────────┐                  ┌─────────────────────────────┐
│ OpenBBMarketDataAdapter     │                  │ MockMarketDataAdapter       │
│ GeminiAdapter (LLM)         │                  │ MockLLMAdapter              │
│ SQLUserRepository           │                  │ MockResearchAdapter         │
│ RedisCacheAdapter           │                  │ MemoryCacheAdapter          │
└─────────────────────────────┘                  └─────────────────────────────┘
```

---

## 2. Injected vs Disconnected Providers

### A. Market Data Subsystem
- **ProviderManager**:
  - `primary_provider`: `OpenBBMarketDataProvider` (Active in DI container).
  - `fallback_providers`: `[YahooMarketDataProvider, NSEMarketDataProvider]`.
  - **Status**: Live quotes & status detection wired. Fundamental, news, macro, and statement methods rely on provider internal stubs.

### B. LLM Subsystem
- **LLMRouter & Factory**:
  - Active Primary: `GeminiAdapter` (`packages/infrastructure/llm/gemini_adapter.py`).
  - Available Secondary Skeletons: `ClaudeAdapter`, `OpenAIAdapter`, `DeepSeekAdapter`, `LocalLLMAdapter`.
  - **Status**: Router fallback mechanism is fully built (`packages/infrastructure/llm/fallback.py`), but secondary API keys and client initializations are unconfigured.

### C. RAG Subsystem
- **Components Built**:
  - `FixedSizeChunker`, `OverlappingChunker` (`packages/rag/chunking/`)
  - `MockEmbeddingAdapter` (`packages/rag/embeddings/mock_embedding_adapter.py`)
  - `InMemoryVectorStore` (`packages/rag/vector_store/in_memory_store.py`)
  - `MockReranker` (`packages/rag/ranking/mock_reranker.py`)
  - `DocumentPipeline` (`packages/rag/pipeline/document_pipeline.py`)
- **Status**: Pipeline is functional in unit tests, but `CompanyDocumentService` in application layer does not call `DocumentPipeline.run()`.

### D. Intelligent Investment Committee Subsystem
- **Components Built**:
  - `CommitteePlanner` (`packages/ai/committee/planner.py`)
  - `CommitteeScheduler` (`packages/ai/committee/scheduler.py`)
  - `CommitteeCritic` (`packages/ai/committee/critic.py`)
  - `CommitteeJudge` (`packages/ai/committee/judge.py`)
  - `InvestmentMemory` (`packages/ai/committee/memory.py`)
  - `IntelligentInvestmentCommittee` (`packages/ai/committee/orchestrator.py`)
- **Status**: Fully tested in isolation, but `CompanyAgentCoordinatorService` (`packages/application/company_intelligence/services.py`) directly invokes individual agents without using the `IntelligentInvestmentCommittee` orchestrator.

---

## 3. Required Wiring Changes for Alpha Production Release

1. **Wire OpenBB SDK Platform to Provider Methods**:
   - Connect `openbb.equity.fundamental.income()`, `balance()`, `cash()` inside `OpenBBMarketDataProvider`.
2. **Wire Application Layer to Intelligent Investment Committee**:
   - Replace `CompanyAgentCoordinatorService` agent loops with `IntelligentInvestmentCommittee.evaluate_company()`.
3. **Wire RAG Document Pipeline to Ingestion & Retrieval**:
   - Inject `DocumentPipeline` into `CompanyDocumentService` to retrieve stored SEBI/Annual Report chunks.
4. **Wire LLM Adapters to Multi-Agent Committee**:
   - Replace `MockLLMAdapter` in non-production with `LLMRouter` managing Gemini and local/secondary fallbacks.
