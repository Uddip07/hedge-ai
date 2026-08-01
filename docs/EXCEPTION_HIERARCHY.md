# Domain Exception Hierarchy Reference

This TDD documentation details the canonical **Domain Exception Hierarchy** implemented in `packages/domain/exceptions/` for the **Indian AI Hedge Fund** platform.

Every domain exception inherits from `DomainError`, guaranteeing structured machine-readable error codes, rich context parameters, metadata payload tracking, and standardized JSON serialization (`to_dict()`).

---

## Class Hierarchy & Error Codes

```text
DomainError (code: DOMAIN_ERROR)
├── ValidationError (code: VALIDATION_ERROR)
│   ├── OrderValidationError (code: ORDER_VALIDATION_ERROR)
│   ├── PositionValidationError (code: POSITION_VALIDATION_ERROR)
│   ├── TickerValidationError (code: TICKER_VALIDATION_ERROR)
│   └── ISINValidationError (code: ISIN_VALIDATION_ERROR)
├── BusinessRuleViolation (code: BUSINESS_RULE_VIOLATION)
│   ├── DuplicateEntityError (code: DUPLICATE_ENTITY)
│   └── EntityNotFoundError (code: ENTITY_NOT_FOUND)
├── MarketError (code: MARKET_ERROR)
│   ├── CorporateActionError (code: CORPORATE_ACTION_ERROR)
│   └── SettlementError (code: SETTLEMENT_ERROR)
├── PortfolioError (code: PORTFOLIO_ERROR)
│   └── InsufficientFundsError (code: INSUFFICIENT_FUNDS)
├── ExecutionError (code: EXECUTION_ERROR)
│   └── BrokerError (code: BROKER_ERROR)
├── RiskViolation (code: RISK_VIOLATION)
├── ResearchError (code: RESEARCH_ERROR)
│   ├── StrategyError (code: STRATEGY_ERROR)
│   └── KnowledgeError (code: KNOWLEDGE_ERROR)
├── AIError (code: AI_ERROR)
└── ConfigurationError (code: CONFIGURATION_ERROR)
```

---

## Detailed Exception Specifications

| Exception Class | Default Code | Description & Usage Context | Typical Context Parameters |
|---|---|---|---|
| **`DomainError`** | `DOMAIN_ERROR` | Root class for all domain errors. | `message`, `code`, `context`, `metadata` |
| **`ValidationError`** | `VALIDATION_ERROR` | Raised when input parameters or value objects fail validation rules. | `field`, `value`, `rule` |
| **`OrderValidationError`** | `ORDER_VALIDATION_ERROR` | Raised when an order fails pre-trade validation checks (e.g. price <= 0). | `order_id`, `ticker`, `order_type` |
| **`PositionValidationError`** | `POSITION_VALIDATION_ERROR` | Raised when position sizing or quantity violates boundaries. | `position_id`, `quantity` |
| **`TickerValidationError`** | `TICKER_VALIDATION_ERROR` | Raised when a ticker string fails regex/exchange parsing. | `ticker_raw` |
| **`ISINValidationError`** | `ISIN_VALIDATION_ERROR` | Raised when an ISIN string fails checksum validation. | `isin_raw` |
| **`BusinessRuleViolation`** | `BUSINESS_RULE_VIOLATION` | Raised when an operation breaches core domain business rules. | `rule_id`, `aggregate_id` |
| **`DuplicateEntityError`** | `DUPLICATE_ENTITY` | Raised when creating an entity with an existing ID in the aggregate. | `entity_id`, `aggregate` |
| **`EntityNotFoundError`** | `ENTITY_NOT_FOUND` | Raised when an entity lookup by ID fails. | `entity_id`, `entity_type` |
| **`MarketError`** | `MARKET_ERROR` | Base exception for exchange or market session errors. | `exchange`, `symbol` |
| **`CorporateActionError`** | `CORPORATE_ACTION_ERROR` | Raised when processing dividends or splits fails. | `action_type`, `symbol` |
| **`SettlementError`** | `SETTLEMENT_ERROR` | Raised when trade clearing or T+1 settlement fails. | `trade_id`, `settlement_date` |
| **`PortfolioError`** | `PORTFOLIO_ERROR` | Base exception for portfolio state anomalies. | `portfolio_id` |
| **`InsufficientFundsError`** | `INSUFFICIENT_FUNDS` | Raised when buying power is insufficient for order value. | `required_cash`, `available_cash` |
| **`ExecutionError`** | `EXECUTION_ERROR` | Base exception for order gateway routing failures. | `order_id`, `gateway` |
| **`BrokerError`** | `BROKER_ERROR` | Raised when broker API rejects an operation. | `broker`, `broker_error_code` |
| **`RiskViolation`** | `RISK_VIOLATION` | Raised when an order breaches VaR, stop loss, or mandate limits. | `mandate_id`, `breach_metric` |
| **`ResearchError`** | `RESEARCH_ERROR` | Base exception for research orchestration failures. | `thesis_id` |
| **`StrategyError`** | `STRATEGY_ERROR` | Raised when strategy signal generation fails. | `strategy_id`, `param` |
| **`KnowledgeError`** | `KNOWLEDGE_ERROR` | Raised when parsing or retrieving documents (SEBI/RBI) fails. | `document_id`, `uri` |
| **`AIError`** | `AI_ERROR` | Raised when LLM reasoning chain or agent execution fails. | `agent_type`, `model` |
| **`ConfigurationError`** | `CONFIGURATION_ERROR` | Raised when system environment or domain config is invalid. | `config_key` |
