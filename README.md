# Indian AI Hedge Fund Platform

> **Institutional-Grade Multi-Agent AI Investment Research, Backtesting & Portfolio Execution Platform for Indian Financial Markets**

[![CI](https://github.com/Uddip07/indian-hedge-fund-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/Uddip07/indian-hedge-fund-ai/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://img.shields.io/badge/mypy-strict-blue)](https://mypy-lang.org/)

---

## 📌 Executive Overview

The **Indian AI Hedge Fund Platform** is an institutional-grade, multi-agent AI investment research, quantitative factor backtesting, and portfolio execution platform specifically engineered for Indian financial markets (**NSE, BSE, MCX**) while remaining globally extensible to international venues (**NYSE, NASDAQ, LSE**).

Built on **Domain-Driven Design (DDD)** and **Clean Architecture** principles, the platform enforces strict separation of concerns, high-precision `Decimal` financial arithmetic, timezone-aware UTC temporal tracking, deterministic backtesting, multi-agent committee consensus, and zero-trust execution safety rules.

---

## 🏛️ Architecture & Core Bounded Contexts

The codebase is organized under `packages/domain/` as a **pure domain model** with zero framework dependencies (no SQLAlchemy, no FastAPI, no HTTP drivers, no broker SDKs inside the domain layer).

```text
packages/domain/
├── enums/             # 33 Domain Enums (ExchangeType, AssetType, OrderType, TaxType, etc.)
├── exceptions/        # 22 Domain Exception Classes derived from DomainError
├── utils/             # High-precision Decimal math and string validation helpers
├── value_objects/     # Immutable Value Objects (Money, Price, Ticker, ISIN, RiskScore, etc.)
├── market/            # Company, Asset, Listing, TradingCalendar, SettlementCycle, OHLCV
├── portfolio/         # Portfolio Aggregate Root, Holding, Position, Trade, RebalancePlan
├── brokerage/         # BrokerAccount Aggregate Root, Order, Execution, MarginRequirement
├── research/          # ResearchReport Aggregate Root, Multi-Agent Consensus, Opinions
├── knowledge/         # KnowledgeBase Aggregate Root, ResearchDocument, AnnualReports
├── strategy/          # Strategy Aggregate Root, Signals, Optimizations, Constraints
├── backtesting/       # Backtest Aggregate Root, BacktestMetrics, TradeLog, EquityCurve
├── ai/                # Prompt Aggregate Root, PromptVersion, ReasoningChain, Traces
├── events/            # 23 Immutable Domain Event Classes (OrderPlaced, TradeExecuted, etc.)
├── repositories/      # 9 Abstract Repository Contracts (ABC) for Persistence
├── policies/          # 7 Domain Business Policies (RiskPolicy, TaxPolicy, ExecutionPolicy)
└── services/          # 7 Stateless Domain Calculators (Sharpe, Volatility, VaR, Returns)
```

---

## 🚀 Quick Start & Development Setup

### Prerequisites
- **Python 3.12+**
- **pip** or **uv** package manager

### 1. Clone the Repository
```bash
git clone https://github.com/Uddip07/indian-hedge-fund-ai.git
cd indian-hedge-fund-ai
```

### 2. Create Virtual Environment & Install Dependencies
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### 3. Run the Full Test Suite & Master Verifier
```bash
# Run complete unit test suite
pytest

# Run master domain layer architecture verifier
python tests/verify_all_domain.py
```

---

## 🧪 Engineering Quality & Tooling

The platform enforces strict static analysis, type checking, formatting, and linting rules defined in `pyproject.toml` and governed by `PROJECT_CONSTITUTION.md`:

```bash
# Code Formatting Check
black --check .

# Linting
ruff check .

# Static Type Checking
mypy packages/domain/

# Pre-commit Hooks Setup
pre-commit install
```

---

## 📜 Repository Governance

This project is governed by explicit engineering laws and workflow standards:

- **[PROJECT_CONSTITUTION.md](PROJECT_CONSTITUTION.md)**: Architectural laws, Python standards, financial precision rules, git workflow conventions, and definition of done.
- **[CONTRIBUTING.md](CONTRIBUTING.md)**: Contribution guidelines and code review standards.
- **[SECURITY.md](SECURITY.md)**: Security vulnerability disclosure policy.
- **[LICENSE](LICENSE)**: Apache License 2.0.

---

## 📄 License

Distributed under the Apache License 2.0. See [LICENSE](LICENSE) for more information.
