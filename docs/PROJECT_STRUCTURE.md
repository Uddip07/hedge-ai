# Project Repository Directory Structure

```
indian-hedge-fund-ai/
├── docs/                             # Architecture, API Contracts, & System Guides
│   ├── api/                          # OpenAPI YAML, API Contract, Endpoint Reference
│   ├── openbb/                       # OpenBB Integration Blueprint & Analyses
│   ├── ARCHITECTURE_VALIDATION.md    # Clean Architecture Invariants Report
│   ├── BACKEND_DEVELOPER_GUIDE.md    # Developer Onboarding Guide
│   ├── COMPANY_INTELLIGENCE_ARCHITECTURE.md # Company Intelligence Engine Spec
│   ├── ENVIRONMENT_VARIABLES.md      # Configuration Reference Manual
│   ├── FRONTEND_INTEGRATION_GUIDE.md # Handoff Guide for Frontend Developers
│   ├── INTELLIGENT_INVESTMENT_COMMITTEE.md # Multi-Agent Committee Spec
│   ├── PERFORMANCE_REVIEW.md         # Latency & Concurrency Audit Report
│   ├── SECURITY_REVIEW.md            # Security & Secret Audit Report
│   └── TESTING_REPORT.md             # Quality Audit & Test Suite Report
├── packages/                         # Monorepo Python Packages
│   ├── ai/                           # AI Core, Committee Engine, Agents, Prompts
│   │   ├── agents/                   # Fundamental, Technical, News, Macro, Risk Agents
│   │   ├── committee/                # Planner, TaskGraph, Scheduler, Critic, Judge, Memory
│   │   └── consensus/                # Weighted Strategy, Conflict Detector, Audit Recorder
│   ├── api/                          # FastAPI Application Layer, Routers, Middlewares
│   │   ├── routers/                  # analyze, market, health, company_intelligence, committee
│   │   └── schemas/                  # Request, Response, Error DTOs
│   ├── application/                  # Use Cases, Commands, Queries, Company Intelligence
│   │   └── company_intelligence/     # Orchestrator, Pipeline, Workflow, ReportBuilder
│   ├── domain/                       # Core Entities, Value Objects, Enums, Exceptions
│   ├── infrastructure/               # Market Data Services, OpenBB Adapter, Registries
│   └── rag/                          # RAG Ingestion Pipeline, Chunking, VectorRetriever
└── tests/                            # Comprehensive Automated Test Suite (292 tests)
```
