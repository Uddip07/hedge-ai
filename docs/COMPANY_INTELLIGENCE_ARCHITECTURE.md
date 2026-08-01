# Company Intelligence Engine Architecture

## 1. Executive Overview

The **Company Intelligence Engine** (`packages/application/company_intelligence/`) delivers institutional-grade equity research reports by orchestrating market intelligence services, RAG document retrieval, multi-agent AI reasoning, consensus engine decisioning, and explainable report assembly.

---

## 2. Core Architecture & Component Responsibilities

```
+-----------------------------------------------------------------------------------+
|                        CompanyIntelligenceOrchestrator                            |
+-----------------------------------------------------------------------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------+
|                         CompanyIntelligenceWorkflow                               |
+-----------------------------------------------------------------------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------+
|                         CompanyIntelligencePipeline                               |
+-----------------------------------------------------------------------------------+
       |                                |                                 |
       v                                v                                 v
+-----------------------+    +-----------------------+    +-------------------------+
| CompanyDataRetrieval  |    |  CompanyDocument      |    | CompanyAgentCoordinator |
|       Service         |    |       Service         |    |         Service         |
+-----------------------+    +-----------------------+    +-------------------------+
       |                                |                                 |
       v                                v                                 v
(Market Data Services)       (RAG VectorRetriever)        (Fundamental, Technical,   |
  Quote, Fundamental,        Annual/Quarterly Reports,     News, Macro, Risk Agents) |
   News, Macro, Actions       Filings Evidence Chunks                     |
                                                                          v
                                                                (ConsensusEngine)
                                                                          |
                                                                          v
+-----------------------------------------------------------------------------------+
|                            ResearchReportBuilder                                  |
+-----------------------------------------------------------------------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------+
|                       ResearchReport (JSON, Markdown, PDF)                        |
+-----------------------------------------------------------------------------------+
```

### Module Responsibilities
- `orchestrator.py`: Application facade entrypoint (`analyze_company`) accepting target tickers.
- `workflow.py`: Manages state execution topology, step validation, and performance timing.
- `pipeline.py`: Executes sequential data retrieval, RAG evidence fetching, agent evaluation, and consensus scoring stages.
- `services.py`:
  - `CompanyDataRetrievalService`: Wraps market infrastructure category services (`QuoteService`, `FundamentalService`, `NewsService`, `MacroService`, `CorporateActionService`, `ExchangeService`).
  - `CompanyDocumentService`: Integrates RAG document ingestion & retrieval pipeline for corporate filings.
  - `CompanyAgentCoordinatorService`: Coordinates 5 specialized agents (`FundamentalAgent`, `TechnicalAgent`, `NewsAgent`, `MacroAgent`, `RiskAgent`) and feeds outputs into `ConsensusEngine`.
- `models.py`: Defines intermediate states, report sections, source attributions, and `ResearchReport` aggregate.
- `report_builder.py`: Transforms compiled pipeline stage outputs into institutional `ResearchReport` instances.
- `exceptions.py`: Standardized domain exceptions (`CompanyIntelligenceError`, `PipelineExecutionError`, `DocumentRetrievalError`, `ReportGenerationError`).

---

## 3. Workflow & Data Flow Topology

1. **Ticker Input & Normalization**: Accepts user input (e.g. `RELIANCE`, `INFY.NSE`, `SBIN.BSE`), normalized via `TickerNormalizer`.
2. **Market Snapshot Retrieval**: Queries real-time price, 24h change, volume, and venue session status (`QuoteService`, `ExchangeService`).
3. **Financial Statements Retrieval**: Queries Income Statement, Balance Sheet, and Cash Flow statement metrics (`FundamentalService`, `CompanyProfileService`).
4. **Technical Analysis Retrieval**: Queries historical OHLCV bars (`HistoricalService`).
5. **News & Sentiment Retrieval**: Queries recent financial news headlines and sentiment scores (`NewsService`).
6. **Corporate Actions Retrieval**: Queries dividends, splits, bonus events (`CorporateActionService`).
7. **Macroeconomic Context**: Queries RBI Repo Rate, inflation, and economic calendar announcements (`MacroService`, `EconomicCalendarService`).
8. **Document Discovery & RAG Retrieval**: Discovers Annual Reports, Quarterly Results, Investor Presentations, and SEBI Filings, returning chunks with metadata source attributions.
9. **Multi-Agent Evaluation**:
   - `FundamentalAgent`: Financial balance sheet & ROCE analysis.
   - `TechnicalAgent`: Price trend momentum analysis.
   - `NewsAgent`: Media headline & sentiment evaluation.
   - `MacroAgent`: Interest rate & macro environment evaluation.
   - `RiskAgent`: Downside risk & governance evaluation.
10. **Consensus Engine Execution**: Aggregates agent votes, applies weights, detects conflicting assumptions/recommendations, computes composite confidence score, generates reasoning graph, and signs audit record.
11. **Explainability & Attribution Assembly**: Constructs evidence citations linking facts to source document IDs, pages, sections, and snippets.
12. **Structured Research Report Assembly**: Constructs `ResearchReport` supporting JSON, GitHub-Flavored Markdown, and PDF metadata exports.

---

## 4. Multi-Agent Coordination & Consensus Engine

- **Specialist Agents**: `FundamentalAgent`, `TechnicalAgent`, `NewsAgent`, `MacroAgent`, `RiskAgent`.
- **Consensus Strategy**: `WeightedConsensusStrategy` computes weighted recommendation scores.
- **Conflict Detection**: `ConflictDetector` identifies contradictory agent votes (e.g. BUY vs SELL), missing evidence, or low confidence.
- **Audit Recording**: `AuditRecorder` computes cryptographically signed SHA-256 audit signatures (`hash_signature`) for regulatory transparency.

---

## 5. Document Intelligence & RAG Integration

- **Filings Supported**: Annual Reports, Quarterly Reports, Investor Presentations, Corporate Announcements, SEBI Filings.
- **Retriever**: `VectorRetriever` returns top-K relevant chunk snippets without whole-document summarization.
- **Attribution**: Every evidence chunk attaches `SourceAttribution` containing `document_id`, `company`, `filing_type`, `section`, `page`, `publication_date`, and `snippet`.

---

## 6. Report Structure, PDF & Dashboard Extensions

### Sections
1. **Executive Summary** (Investment thesis, key strengths, primary risks, target horizon, final recommendation).
2. **Market Snapshot** (Price, 24h change, volume, venue, session open).
3. **Financial Highlights** (Total Revenue, Net Income, Total Assets, Total Liabilities, Operating Cash Flow, Free Cash Flow).
4. **Technical Analysis** (Timeframe, bar count, trend summary, last close).
5. **Recent News & Sentiment** (Article count, sentiment score, headlines, sources).
6. **Corporate Actions** (Actions count, event breakdown).
7. **Macroeconomic Context** (Series name, repo rate, upcoming events).
8. **Multi-Agent Committee Opinions** (Individual agent recommendations, scores, confidence, reasoning).
9. **Consensus Decision** (Winning recommendation, consensus score, composite confidence, agreement ratio, conflict count, audit session ID).
10. **Explainability & Evidence Attribution** (Reasoning trace, evidence citations, bull case, bear case, assumptions, unknowns, key risks).

### Output Formats
- `.to_json()`: Machine-readable JSON output for APIs and downstream analytical systems.
- `.to_markdown()`: Human-readable GitHub-Flavored Markdown report.
- `.to_pdf_metadata()`: PDF layout metadata prepared for report rendering engines (e.g., ReportLab / WeasyPrint).
- **Future Dashboard Integration**: JSON schema matches UI workbench state contracts for real-time frontend dashboard rendering.
