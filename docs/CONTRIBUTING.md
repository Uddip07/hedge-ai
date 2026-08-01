# Contributing Guidelines

Thank you for your interest in contributing to the **Indian AI Hedge Fund Platform**!

This project adheres strictly to **Domain-Driven Design (DDD)**, **Clean Architecture**, and the engineering laws codified in [PROJECT_CONSTITUTION.md](PROJECT_CONSTITUTION.md).

---

## 📜 Principles & Standards

Before submitting any Pull Request or issue, please read [PROJECT_CONSTITUTION.md](PROJECT_CONSTITUTION.md). Key laws include:

1. **Pure Domain Layer**: `packages/domain/` MUST remain 100% pure Python standard library code (zero external framework or driver imports).
2. **Financial Precision**: **NEVER use `float` for money or currency calculations.** Always use `decimal.Decimal`.
3. **Timezone Awareness**: All timestamps must be timezone-aware (default `datetime.timezone.utc`).
4. **Immutability**: Value Objects and Domain Events must be frozen dataclasses (`@dataclass(frozen=True, slots=True)`).
5. **Quality Checks**: Code must pass `black --check .`, `ruff check .`, `mypy packages/domain/`, and all unit tests cleanly.

---

## 🛠️ Development Setup

1. **Fork and Clone the Repository**:
   ```bash
   git clone https://github.com/<your-username>/indian-hedge-fund-ai.git
   cd indian-hedge-fund-ai
   ```

2. **Setup Virtual Environment & Development Tooling**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e ".[dev]"
   pre-commit install
   ```

3. **Verify Existing Tests & Master Domain Architecture**:
   ```bash
   pytest
   python tests/verify_all_domain.py
   ```

---

## 🌿 Git Branching & Commit Message Conventions

### Branch Naming
All feature branches must follow the prefix pattern:
- `feature/description` (e.g., `feature/option-greeks-calculator`)
- `bugfix/description` (e.g., `bugfix/stcg-tax-bracket-fix`)
- `refactor/description` (e.g., `refactor/rebalance-plan-validation`)
- `docs/description` (e.g., `docs/add-adr-002`)
- `hotfix/description` (e.g., `hotfix/isin-checksum-validation`)

### Commit Messages
Commit messages must follow the [Conventional Commits](https://www.conventionalcommits.org/) format:
- `feat: add Black-Scholes Option Greeks calculator`
- `fix: resolve equity curve drawdown computation`
- `refactor: optimize holding weight calculations`
- `docs: update research policy documentation`
- `test: add unit tests for BrokerAccount margin calls`

---

## 📥 Pull Request Process

1. Create an issue using the appropriate template under `.github/ISSUE_TEMPLATE/` prior to working on major features.
2. Implement your changes following DDD principles.
3. Ensure all tests and static checks pass cleanly:
   ```bash
   black .
   ruff check --fix .
   mypy packages/domain/
   pytest
   python tests/verify_all_domain.py
   ```
4. Submit your Pull Request using `.github/PULL_REQUEST_TEMPLATE.md`.
5. Ensure all mandatory checklist items in the PR template are completed.

---

## 📋 Code Review Guidelines

Every Pull Request is audited against the 10-point checklist in `PROJECT_CONSTITUTION.md`:
1. Architecture Alignment (Clean Architecture & DDD boundaries)
2. DDD Principles & Invariant Protection
3. Type Hinting Completeness (`mypy --strict`)
4. Unit Testing Coverage & Failure Mode Tests
5. Performance & Efficiency
6. Security Standard (No hardcoded secrets)
7. Documentation Clarity (PEP 257 docstrings)
8. Naming Discipline (PEP 8)
9. Explicit Error Handling (`DomainError` subclasses)
10. Maintainability & DoD Compliance
