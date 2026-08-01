# System-Wide Data Flow Map

> **Document Version**: 1.0.0  
> **Status**: APPROVED DATA FLOW BLUEPRINT  
> **Target System**: MONEYYYYYY Engine  

---

## 1. Subsystem Data Flow Maps

### 1. Market Quote Flow
```
User / Frontend
   │
   ▼
GET /market/{ticker} [packages/api/routers/market.py]
   │
   ▼
ProviderManager.get_quote() [packages/infrastructure/market_data/provider_manager.py]
   ├── Check MarketDataCache [packages/infrastructure/market_data/cache.py]
   │     └── (Hit) ──► Return Cached Quote
   ├── (Miss) ──► OpenBBMarketDataProvider.get_quote()
   │                 ├── (Success) ──► Cache & Return Quote
   │                 └── (Error) ──► YahooMarketDataProvider.get_quote() (Fallback)
   │                                    └── (Error) ──► NSEMarketDataProvider.get_quote() (Fallback)
   └── (All Fail) ──► Serve Stale Cache or Raise RuntimeError
```

### 2. Company Intelligence Workflow Flow
```
User / Frontend
   │
   ▼
GET /company-intelligence/{ticker} [packages/api/routers/company_intelligence.py]
   │
   ▼
CompanyIntelligenceOrchestrator.analyze_company() [packages/application/company_intelligence/orchestrator.py]
   │
   ├── 1. Market Data Retrieval (CompanyDataRetrievalService)
   │        ├── Snapshot ──► ProviderManager
   │        ├── Financial Highlights ──► FundamentalService
   │        ├── Technical Analysis ──► HistoricalService
   │        ├── News ──► NewsService
   │        ├── Corporate Actions ──► CorporateActionService
   │        └── Macro Context ──► MacroService
   │
   ├── 2. RAG Document Ingestion & Evidence Retrieval (CompanyDocumentService)
   │        ├── DocumentManager ──► Load Annual Reports / Filings
   │        ├── DocumentPipeline ──► Chunker -> Embeddings -> VectorStore
   │        └── VectorRetriever ──► Query Top-K Evidence Chunks
   │
   └── 3. Multi-Agent Committee Evaluation (CompanyAgentCoordinatorService)
            ├── Agent Context Building (AgentContext)
            ├── Agents Execution (Fundamental, Technical, News, Macro, Risk)
            └── ConsensusEngine ──► ConsensusIntelligenceDecision & Explainability
```

### 3. Multi-Agent Committee Execution Flow
```
CompanyAgentCoordinatorService.evaluate_committee()
   │
   ▼
IntelligentInvestmentCommittee.evaluate_company() [packages/ai/committee/orchestrator.py]
   ├── CommitteePlanner ──► Build TaskGraph for target timeframe
   ├── CommitteeScheduler ──► Execute Agents concurrently (Fundamental, Technical, News, Macro, Risk)
   ├── CommitteeCritic ──► Audit opinions for bias & conflict
   ├── CommitteeJudge ──► Compute final weighted consensus score
   ├── InvestmentMemory ──► Store session decision & reasoning history
   └── Return Results & Consensus Intelligence Decision
```

---

## 2. Dependency Graphs

### Market Subsystem Graph
`packages/api/routers/market.py`  
  └─► `packages/api/dependencies.py`  
        └─► `packages/infrastructure/market_data/provider_manager.py`  
              ├─► `packages/domain/market/quote.py`  
              ├─► `packages/infrastructure/market_data/cache.py`  
              ├─► `packages/infrastructure/market_data/providers/openbb_provider.py`  
              ├─► `packages/infrastructure/market_data/providers/yahoo_provider.py`  
              └─► `packages/infrastructure/market_data/providers/nse_provider.py`

### Company Intelligence Subsystem Graph
`packages/api/routers/company_intelligence.py`  
  └─► `packages/application/company_intelligence/orchestrator.py`  
        ├─► `packages/application/company_intelligence/services.py`  
        │     ├─► `CompanyDataRetrievalService`  
        │     ├─► `CompanyDocumentService`  
        │     └─► `CompanyAgentCoordinatorService`  
        ├─► `packages/ai/consensus/engine.py`  
        └─► `packages/rag/pipeline/document_pipeline.py`
