# API Endpoint Reference Manual

## 1. Status & Health Endpoints

### `GET /`
- **Purpose**: System identification and top-level execution status.
- **Query Params**: None
- **Response**: `RootResponse` (200 OK)

### `GET /health`
- **Purpose**: Diagnostic health check across database, cache, and platform subsystems.
- **Response**: `HealthResponse` (200 OK)

### `GET /version`
- **Purpose**: Returns software version and build environment metadata.
- **Response**: `VersionResponse` (200 OK)

---

## 2. Market Intelligence Endpoints

### `GET /market/{ticker}`
- **Purpose**: Retrieve current market quote, price, 24h volume, exchange venue, and company profile.
- **Path Parameters**:
  - `ticker` (string, required): Ticker symbol (e.g. `RELIANCE`, `TCS.NSE`, `INFY.BSE`).
- **Response**: Market Quote JSON Payload (200 OK)
- **Errors**: 422 Unprocessable Entity (Invalid ticker format).

---

## 3. Investment Research & Intelligence Endpoints

### `POST /analyze`
- **Purpose**: Single-stock analysis use case execution.
- **Request Body**: `AnalyzeStockRequest`
- **Response**: `AnalyzeStockResponse` (200 OK)

### `GET /company-intelligence/{ticker}`
- **Purpose**: Generates an institutional end-to-end company intelligence research report.
- **Path Parameters**:
  - `ticker` (string, required): Target ticker symbol.
- **Response**: `CompanyIntelligenceResponse` (200 OK)

### `POST /committee/evaluate`
- **Purpose**: Triggers Planner, Task Graph execution, 5 Specialist Agents, Adversarial Critic, Judicial Evaluation, and Consensus Engine decisioning.
- **Request Body**: `EvaluateCommitteeRequest`
- **Response**: `EvaluateCommitteeResponse` (200 OK)
