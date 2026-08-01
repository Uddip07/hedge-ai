# Codebase Overview & System Architecture Walkthrough

## 1. Subsystem Architecture
- **Domain Layer (`packages/domain/`)**: Immutable value objects (`Price`, `Money`, `Ticker`), Entities (`Company`, `MarketQuote`), and Domain Enums (`ExchangeType`, `Timeframe`, `RecommendationType`, `AgentType`). Pure Python with zero external dependencies.
- **Market Intelligence Infrastructure (`packages/infrastructure/market_data/`)**: 11 modularized category services (`QuoteService`, `FundamentalService`, `NewsService`, `MacroService`, `ExchangeService`, etc.) backed by OpenBB adapter and multi-provider registries.
- **RAG Document Pipeline (`packages/rag/`)**: Parser, Fixed/Overlapping Chunkers, In-Memory & HNSW Vector Store adapters, and VectorRetriever returning source-attributed evidence snippets.
- **Company Intelligence Engine (`packages/application/company_intelligence/`)**: Orchestrates market data, RAG filing discovery, 5 specialist AI agents, and consensus calculation to render institutional research reports.
- **Intelligent Investment Committee (`packages/ai/committee/`)**: Central reasoning brain featuring Planner, DAG TaskGraph, Parallel Scheduler, Adversarial Critic, Judicial Evaluator, Consensus Engine integration, and Persistent Investment Memory.
- **REST API Layer (`packages/api/`)**: FastAPI web platform exposing REST endpoints, CORS middleware, timing logging, and standardized error schemas.
