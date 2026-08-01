# Unused Infrastructure & Dead Code Inventory

> **Document Version**: 1.0.0  
> **Status**: APPROVED DEAD CODE AUDIT  
> **Target System**: MONEYYYYYY Engine  

---

## 1. Unused & Orphaned Infrastructure Components

1. **`ClaudeAdapter`**:
   - Location: `packages/infrastructure/llm/providers/claude/adapter.py`
   - Reason: Implements `LLMPort` interface skeleton, but has no API key parsing or live client initialization in `DIContainer`.
2. **`OpenAIAdapter`**:
   - Location: `packages/infrastructure/llm/providers/openai/adapter.py`
   - Reason: Implements `LLMPort` interface skeleton, but is unreferenced in container setup.
3. **`DeepSeekAdapter`**:
   - Location: `packages/infrastructure/llm/providers/deepseek/adapter.py`
   - Reason: Implements `LLMPort` interface skeleton, unreferenced in container setup.
4. **`LocalLLMAdapter`**:
   - Location: `packages/infrastructure/llm/providers/local/adapter.py`
   - Reason: Local Ollama wrapper unreferenced in active runtime setup.
5. **`MockBrokerAdapter`**:
   - Location: `packages/infrastructure/adapters/mock_broker_adapter.py`
   - Reason: Active in development DI mode; needs paper trading broker adapter replacement.
6. **`MockStorageAdapter`**:
   - Location: `packages/infrastructure/adapters/mock_storage_adapter.py`
   - Reason: Active in development DI mode; needs S3/GCS cloud storage adapter replacement.

---

## 2. Standalone Services Needing Application Integration

1. **`IntelligentInvestmentCommittee`**:
   - Location: `packages/ai/committee/orchestrator.py`
   - Status: Fully implemented; needs to replace basic agent execution loop in `CompanyAgentCoordinatorService`.
2. **`DocumentPipeline` & `VectorRetriever`**:
   - Location: `packages/rag/pipeline/document_pipeline.py`, `packages/rag/retriever/vector_retriever.py`
   - Status: Fully implemented; needs to replace synthetic RAG chunk creation in `CompanyDocumentService`.
3. **OpenBB Secondary Category Services**:
   - Location: `packages/infrastructure/market_data/services/`
   - Status: Implemented; needs OpenBB SDK live data methods bound in `OpenBBMarketDataProvider`.
