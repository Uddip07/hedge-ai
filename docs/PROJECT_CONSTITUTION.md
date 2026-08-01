# PROJECT CONSTITUTION

> **Engineering Law & Architectural Governance**  
> *Indian AI Hedge Fund & Investment Research Platform*

---

## 1. Project Vision

The primary mission of this project is to build an institutional-grade, multi-agent AI-powered investment research, quantitative backtesting, and portfolio management platform.

- **Primary Focus**: Indian Financial Markets (NSE, BSE, MCX) with explicit compliance and domain alignment for SEBI regulations, RBI policies, Indian tax structures (STT, STCG 20%, LTCG 12.5%, Section 194 TDS), and domestic corporate action mechanics.
- **Global Extensibility**: Bounded contexts, asset schemas, and market data interfaces are architected to support global execution venues (NYSE, NASDAQ, LSE) and multi-asset asset classes (Equities, ETFs, Derivatives, REITs, InvITs, Fixed Income) without refactoring domain boundaries.
- **Institutional Governance**: Prioritizes deterministic financial arithmetic, complete auditability, multi-agent committee consensus, and zero-trust execution safety over prompt-only heuristics.

---

## 2. Architecture Principles

1. **Domain-Driven Design (DDD)**:
   - The domain model is the ultimate source of business truth.
   - Strict separation between Aggregate Roots, Entities, Value Objects, Domain Events, Domain Policies, and Repository Interfaces.
   - Aggregate Roots strictly enforce internal entity ownership and invariant consistency.
2. **Clean Architecture**:
   - Explicit dependency flow: `UI / API / CLI` → `Application / Use Cases` → `Domain`.
   - The core domain layer (`packages/domain/`) has **zero dependencies** on external frameworks, databases, or network protocols.
3. **SOLID Principles**:
   - **Single Responsibility**: Each module, class, or service owns a single well-defined responsibility.
   - **Open/Closed**: Extensible for new asset types or calculation models via abstract contracts without modifying existing code.
   - **Liskov Substitution**: Derived classes and concrete repository implementations must fulfill all parent contract invariants without side effects.
   - **Interface Segregation**: Focused, narrow interfaces over generic monolithic contracts.
   - **Dependency Inversion**: High-level domain services depend on abstract protocols and interfaces (`abc.ABC`), never on concrete infrastructure drivers.
4. **Explicit Dependencies & Inversion of Control**:
   - No hidden global singletons or ambient magic state. Dependencies are explicitly passed via constructor injection.
5. **Composition Over Inheritance**:
   - Prefer composing behavior through components and value objects over deep inheritance hierarchies (with the exception of domain exceptions and base domain event structures).
6. **Event-Driven Architecture**:
   - State transitions and domain facts produce immutable `DomainEvent` instances for decoupled event processing, audit logging, and telemetry tracking.

---

## 3. Engineering Principles

1. **Readability Over Cleverness**:
   - Code must be written for clarity, readability, and long-term maintainability. Avoid obscure pythonic tricks, dynamic attribute injection, or unreadable inline lambdas.
2. **Maintainability Over Short Code**:
   - Explicit parameter names, comprehensive type signatures, and clear control flow are mandated. Concise code is a secondary goal compared to correctness and maintainability.
3. **Strong Typing & Static Analysis**:
   - Strict type hints on every function, method, class attribute, and variable. No implicit `Any` types allowed.
4. **Pure Domain Layer**:
   - All code inside `packages/domain/` must be 100% pure Python standard library code.
5. **High Cohesion & Low Coupling**:
   - Related financial concepts sit together within their respective bounded contexts; cross-context references must be minimized and decoupled via identifiers or domain events.
6. **No Hidden Side Effects**:
   - Functions and methods must be predictable. Value Objects are strictly side-effect free. Domain services must explicitly state state mutations.

---

## 4. Python Standards

1. **Python Version**: Strictly **Python 3.12+**.
2. **Type Annotations**:
   - Complete type coverage enforced by `mypy --strict`.
   - Use standard library generics (`list[str]`, `dict[str, Any]`, `tuple[int, ...]`, `Callable[[X], Y]`).
3. **Formatting & Linting**:
   - Enforce **PEP 8** style guidelines using `ruff` and `black`.
   - Maximum line length: **100 characters**.
4. **Docstrings & Documentation**:
   - Enforce **PEP 257** docstring conventions for all public classes, methods, modules, and functions.
5. **Financial Calculations**:
   - **NEVER use `float` for monetary or currency calculations.** Always use `decimal.Decimal`.
   - Use explicit rounding modes: `ROUND_HALF_UP` for currency representation.
6. **Temporal Calculations**:
   - **NEVER use naive `datetime` objects.** All timestamps must be timezone-aware (default `datetime.timezone.utc`).
7. **Dataclasses & Immutability**:
   - Use `@dataclass(frozen=True, slots=True)` for Value Objects and Domain Events.
8. **Abstract Contracts**:
   - Define interfaces using `abc.ABC` with `@abstractmethod` or `typing.Protocol`.

---

## 5. Financial Software Standards

1. **Monetary Precision**:
   - Monetary values (`Money`, `Price`, `Margin`, `Exposure`) must be instantiated using `Decimal` or string representations (e.g., `Decimal("2500.50")`). Floating-point instantiation is forbidden.
2. **External Input Validation**:
   - All external data (API payloads, broker tick streams, user inputs, CSV/Parquet uploads) must pass through domain validation layers before reaching entities.
3. **Immutable Value Objects**:
   - Value Objects (`Money`, `Price`, `Ticker`, `ISIN`, `Quantity`, `Percentage`, `Weight`, `Timestamp`, etc.) cannot be mutated post-instantiation.
4. **Auditability & Traceability**:
   - Every financial order placement, trade fill execution, portfolio rebalance, and risk override must be accompanied by an immutable audit record and event trail.
5. **Deterministic Calculations**:
   - Given identical historical market inputs, quantitative models, backtesting engines, and portfolio calculators must produce 100% bit-identical results.
6. **Idempotent Operations**:
   - Execution commands, event handlers, and trade loggers must support idempotent execution to prevent duplicate trade orders or double-counting cash balances.
7. **Explicit Error Handling**:
   - Fail fast on domain invariant breaches using explicit domain exception subclasses derived from `DomainError`. Silent exception swallowing is illegal.

---

## 6. Domain Rules

1. **Zero Infrastructure Dependencies in Domain**:
   - `packages/domain/` MUST NOT import external frameworks or drivers:
     - ❌ No `SQLAlchemy`, `SQLModel`, `Peewee`, or ORM annotations.
     - ❌ No `FastAPI`, `Starlette`, `Flask`, or HTTP client libraries (`httpx`, `requests`).
     - ❌ No broker SDKs (`dhanhq`, `shoonya`, `zerodha_kite`, `ib_insync`).
     - ❌ No third-party AI provider SDKs (`openai`, `anthropic`, `google-genai`).
2. **Zero Circular Imports**:
   - Circular module dependencies are completely forbidden. Dependencies must flow downward from value objects and enums to entities, aggregate roots, policies, services, and repositories.
3. **Aggregate Root Ownership Rules**:
   - Aggregates (e.g., `Portfolio`, `BrokerAccount`, `Strategy`, `ResearchReport`, `KnowledgeBase`, `Backtest`, `Prompt`) manage their internal entities directly. External callers must modify child entities strictly through Aggregate Root methods.
4. **Entities Contain Business Behavior**:
   - Entities are not passive data bags. They encapsulate active domain rules, invariants, and business methods (e.g., `Portfolio.execute_trade()`, `BrokerAccount.submit_order()`).
5. **Immutable Value Objects**:
   - Value Objects implement structural equality (`__eq__`, `__hash__`) and self-validation upon instantiation.

---

## 7. Testing Standards

1. **Unit Testing Mandate**:
   - Every domain model, value object, policy, calculator service, and exception must have thorough unit tests using `pytest` or `unittest`.
2. **Static Type Checking**:
   - `mypy --strict` must run in CI and pass cleanly without type errors or warnings.
3. **Linting & Code Quality**:
   - `ruff check .` and `black --check .` must pass cleanly prior to merging.
4. **Regression Testing**:
   - Every identified bug or edge case must be accompanied by a dedicated regression test reproducing the issue before the fix is applied.
5. **High Coverage Goal**:
   - Maintain >= 90% code coverage across domain packages (`packages/domain/`).

---

## 8. Git Workflow

### Branch Naming Conventions
All branches created must follow the structured prefix naming pattern:

- `feature/description` (e.g., `feature/portfolio-rebalance-calculator`)
- `bugfix/description` (e.g., `bugfix/drawdown-peak-calculation`)
- `refactor/description` (e.g., `refactor/consensus-score-aggregation`)
- `docs/description` (e.g., `docs/project-constitution`)
- `hotfix/description` (e.g., `hotfix/tds-tax-rate-adjustment`)

### Commit Message Conventions
Commit messages must follow the Conventional Commits specification:

- `feat: add STCG and LTCG tax policy calculation`
- `fix: resolve equity curve peak-to-trough drawdown calculation`
- `refactor: optimize portfolio holding weight calculator`
- `docs: update domain repository architecture specification`
- `test: add unit tests for BrokerAccount margin calls`
- `chore: update mypy configuration`
- `perf: optimize vectorized candle calculations`

---

## 9. Pull Request Rules

Every Pull Request submitted must use `.github/PULL_REQUEST_TEMPLATE.md` and explicitly include:

1. **Summary**: Clear description of what changes are introduced.
2. **Motivation**: Business or technical rationale driving the change.
3. **Implementation Details**: Concise technical summary of code modifications.
4. **Testing Performed**: Commands executed and test results verifying correctness.
5. **Checklist**: Mandatory completion of type checking, linting, tests, and documentation checks.
6. **Breaking Changes**: Explicit statement of any breaking contract changes and migration guidance.
7. **UI Screenshots / Demos**: Embedded screenshots or recordings if UI changes are included.

---

## 10. Code Review Checklist

Code reviewers must audit every Pull Request against these 10 criteria:

1. **Architecture Alignment**: Respects Clean Architecture, DDD boundaries, and layer separation.
2. **DDD Principles**: Entities enforce invariants; Value Objects remain immutable; Aggregates maintain consistency.
3. **Typing Completeness**: Strict Python 3.12 type hints without implicit `Any` or missing parameters.
4. **Testing Rigor**: Unit tests accompany all changes; edge cases and failure modes covered.
5. **Performance Efficiency**: Avoids unnecessary computational complexity, nested loops, or excessive memory allocations.
6. **Security Standard**: No hardcoded API keys, secrets, or unvalidated inputs.
7. **Documentation Clarity**: Public APIs, classes, and complex algorithms fully documented with PEP 257 docstrings.
8. **Naming Discipline**: Clear, self-describing variable, function, and class names reflecting domain terms.
9. **Error Handling**: Uses domain-specific exception classes; fails fast with informative context.
10. **Maintainability**: Clean, readable code without obscure hacks or unnecessary dependencies.

---

## 11. Definition of Done (DoD)

A task, feature, or pull request is considered **DONE** only when:

- [ ] Code compiles without syntax or import errors.
- [ ] All automated unit tests pass 100% cleanly.
- [ ] Linting (`ruff check .`, `black --check .`) passes with zero violations.
- [ ] Static type checking (`mypy`) passes with zero type errors.
- [ ] Architecture and public API documentation has been updated.
- [ ] Zero `TODO`, `FIXME`, or placeholder methods remain in production code.
- [ ] Domain Model architecture and Clean Architecture boundaries remain strictly preserved.

---

## 12. Security Principles

1. **Zero Secret Hardcoding**:
   - NEVER commit secrets, passwords, private keys, or API credentials into source code.
2. **Environment Variable Configuration**:
   - All runtime credentials and environment variables must be loaded via secure configuration interfaces.
3. **Input Sanitization & Validation**:
   - All external inputs (JSON payloads, file uploads, prompt variables) must be sanitized and validated before execution.
4. **Principle of Least Privilege**:
   - Broker API credentials, storage access tokens, and AI model API keys must operate under minimum necessary permission scopes.
5. **Safe Data Serialization**:
   - Avoid unsafe deserialization functions (`pickle`, `eval`). Use structured JSON or typed dataclass serialization.

---

## 13. Documentation Rules

1. **Public API Documentation**:
   - Every public module, class, interface, method, and function must have a comprehensive PEP 257 docstring explaining its purpose, parameters, return values, and raised exceptions.
2. **Architectural Decisions**:
   - Significant technical design choices, structural changes, or domain trade-offs must be formally documented as Architecture Decision Records (ADR).
3. **Complex Algorithm Explanations**:
   - Financial algorithms (e.g., VaR, Sharpe, Sortino, consensus aggregation) must include inline comments or docstring mathematical explanations.

---

## 14. Architecture Decision Record (ADR) Policy

- All major architectural decisions, layer restructuring, database schema selections, framework integrations, or domain boundary changes **MUST** be documented inside the repository under `docs/adr/`.
- ADR documents must follow the standard structure:
  - **Title**: Sequential identifier and clear title (e.g., `ADR-001-pure-domain-layer-isolation.md`).
  - **Status**: Proposed / Accepted / Superseded / Deprecated.
  - **Context**: Problem statement and technical background.
  - **Decision**: The chosen architectural path.
  - **Consequences**: Positive, negative, and neutral trade-offs resulting from the decision.
