# Phase 1 Implementation Plan: Mock Replacement Roadmap

> **Document Version**: 1.0.0  
> **Status**: APPROVED IMPLEMENTATION ROADMAP  
> **Target Milestone**: ALPHA MOCK-REPLACEMENT MILESTONE  

---

## Task Roadmap Overview

```
 ┌────────────────────────────────────────────────────────┐
 │ TASK 1: Live OpenBB Fundamentals & Financial Statements │
 └───────────────────────────┬────────────────────────────┘
                             │
 ┌───────────────────────────▼────────────────────────────┐
 │ TASK 2: Intelligent Committee Orchestrator Wiring      │
 └───────────────────────────┬────────────────────────────┘
                             │
 ┌───────────────────────────▼────────────────────────────┐
 │ TASK 3: RAG Production Document Ingestion & Vector Rerank│
 └───────────────────────────┬────────────────────────────┘
                             │
 ┌───────────────────────────▼────────────────────────────┐
 │ TASK 4: Secondary LLM Provider Failover Configuration  │
 └────────────────────────────────────────────────────────┘
```

---

## Detailed Task Breakdown

### Task 1: Wire Live OpenBB Fundamentals & Financial Statements
- **Objective**: Replace all synthetic balance sheets, income statements, cash flows, and company profiles with live OpenBB SDK data feeds.
- **Priority**: P0
- **Complexity**: High
- **Files Affected**:
  - `packages/infrastructure/market_data/providers/openbb_provider.py`
  - `packages/infrastructure/openbb/adapter.py`
  - `packages/application/company_intelligence/services.py`
- **Dependencies**: OpenBB Platform SDK (`openbb>=4.0.0`)
- **Breaking Change Risk**: Low (Preserves existing DTO schemas).
- **Testing Requirements**: Integration tests with mocked OpenBB SDK client and live market fixtures.

---

### Task 2: Wire Intelligent Committee Orchestrator to Company Intelligence
- **Objective**: Replace hardcoded agent loops in `CompanyAgentCoordinatorService` with `IntelligentInvestmentCommittee.evaluate_company()`.
- **Priority**: P0
- **Complexity**: High
- **Files Affected**:
  - `packages/application/company_intelligence/services.py`
  - `packages/api/dependencies.py`
- **Dependencies**: Gemini LLM Adapter / LLMRouter
- **Breaking Change Risk**: Medium (Requires matching structured consensus responses).
- **Testing Requirements**: Multi-agent integration tests with `GeminiAdapter`.

---

### Task 3: Wire Production RAG Document Ingestion & Retrieval
- **Objective**: Replace synthetic RAG chunks with live `DocumentPipeline` chunking, embedding, vector store retrieval, and re-ranking.
- **Priority**: P0
- **Complexity**: Medium
- **Files Affected**:
  - `packages/application/company_intelligence/services.py`
  - `packages/rag/pipeline/document_pipeline.py`
- **Dependencies**: Vector store & embedding adapter
- **Breaking Change Risk**: Low
- **Testing Requirements**: End-to-end RAG ingestion & vector search unit tests.

---

### Task 4: Configure Secondary LLM Provider Adapters in LLMRouter
- **Objective**: Wire `ClaudeAdapter`, `OpenAIAdapter`, `DeepSeekAdapter`, and `LocalLLMAdapter` into `LLMRouter` for automatic fallback.
- **Priority**: P1
- **Complexity**: Medium
- **Files Affected**:
  - `packages/infrastructure/dependency_injection/container.py`
  - `packages/infrastructure/llm/fallback.py`
- **Dependencies**: Third-party API credentials
- **Breaking Change Risk**: Low
- **Testing Requirements**: Multi-provider fallback router unit tests.
