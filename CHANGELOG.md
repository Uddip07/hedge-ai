# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-07-24

### Added
- Initial **Pure Domain Layer** implementation (`packages/domain/`) following Domain-Driven Design (DDD) and Clean Architecture principles:
  - `enums`: 33 domain enums (`ExchangeType`, `AssetType`, `OrderType`, `OrderStatus`, `TradeType`, `PositionType`, `MarketSegment`, `MarketSession`, `SettlementType`, `TaxType`, `PortfolioType`, `AgentType`, etc.).
  - `exceptions`: 22 exception classes derived from `DomainError`.
  - `utils`: High-precision `Decimal` financial arithmetic and string validation helpers.
  - `value_objects`: Core (`Money`, `Price`, `Quantity`, `Percentage`, `Weight`, `Allocation`), Identifiers (`Ticker`, `ISIN`, `PortfolioId`, `OrderId`, `TradeId`, etc.), Metrics (`RiskScore`, `ConfidenceScore`, `SharpeRatio`, `SortinoRatio`, `Drawdown`, `Volatility`), and Temporal (`Timestamp`, `MarketTimestamp`, `TradingDate`, `FiscalYear`, `ReportingPeriod`, `PriceRange`).
  - `market`: Entities for `Company`, `Asset`, `Listing`, `TradingCalendar`, `TradingSession`, `MarketHoliday`, `SettlementCycle`, `OHLCV`, `Candle`.
  - `portfolio`: `Portfolio` Aggregate Root, `Holding`, `Position`, `Trade`, `PortfolioSnapshot`, `PerformanceSnapshot`, `RebalancePlan`.
  - `brokerage`: `BrokerAccount` Aggregate Root, `Order`, `Execution`, `AccountBalance`, `MarginRequirement`.
  - `research`: `ResearchReport` Aggregate Root, `FundamentalAnalysis`, `TechnicalAnalysis`, `MacroAnalysis`, `SentimentAnalysis`, `AgentOpinion`, `ConsensusDecision`, `FinalRecommendation`.
  - `knowledge`: `KnowledgeBase` Aggregate Root, `ResearchDocument`, and 8 specialized document types (`AnnualReport`, `NewsArticle`, `SEBICircular`, `RBIReport`, `BudgetDocument`, `Transcript`, `ResearchNote`, `PDFDocument`).
  - `strategy`: `Strategy` Aggregate Root, `StrategyVersion`, `Signal`, `SignalResult`, `Optimization`, `Constraint`, `Parameter`, `ObjectiveFunction`, `EvaluationResult`.
  - `backtesting`: `Backtest` Aggregate Root, `BacktestRun`, `BacktestMetrics`, `TradeLog`, `EquityCurve`, `BacktestResult`.
  - `ai`: `Prompt` Aggregate Root, `PromptVersion`, `PromptExecution`, `ReasoningChain`, `ReasoningTrace`, `Evidence`, `Citation`, `ToolInvocation`, `AgentDecision`, `ModelResponse`.
  - `events`: `DomainEvent` base class and 22 immutable domain event classes.
  - `repositories`: 9 abstract repository contracts (`abc.ABC`).
  - `policies`: 7 domain business policies (`RiskPolicy`, `ExecutionPolicy`, `PortfolioPolicy`, `AllocationPolicy`, `DividendPolicy`, `TaxPolicy`, `ResearchPolicy`).
  - `services`: 7 stateless domain calculators (`PortfolioCalculator`, `RiskCalculator`, `ConsensusCalculator`, `RecommendationAggregator`, `DrawdownCalculator`, `SharpeCalculator`, `ReturnCalculator`).
- Repository Governance & Engineering Infrastructure:
  - `PROJECT_CONSTITUTION.md` establishing engineering law and architecture rules.
  - GitHub issue templates (`bug_report.md`, `feature_request.md`, `engineering_task.md`, `architecture_review.md`).
  - GitHub pull request template (`PULL_REQUEST_TEMPLATE.md`).
  - GitHub Actions CI workflow (`.github/workflows/ci.yml`).
  - Packaging & tool configurations (`pyproject.toml`, `.editorconfig`, `.pre-commit-config.yaml`).
  - Project governance metadata (`README.md`, `LICENSE`, `SECURITY.md`, `CONTRIBUTING.md`, `.github/CODEOWNERS`).
- Comprehensive unit test suite (`tests/domain/`, 129 passing tests) and master verifier script (`tests/verify_all_domain.py`).
