# Application Layer

> **Clean Architecture & CQRS Foundation**  
> *Indian AI Hedge Fund & Investment Research Platform*

---

## 1. Overview

The `packages/application/` package forms the application layer of the system under Clean Architecture. It encapsulates all application workflow orchestration, CQRS command and query models, Data Transfer Objects (DTOs), interface mappers, application services, and outbound port contracts.

---

## 2. Command Query Responsibility Segregation (CQRS)

This application layer strictly enforces the **CQRS (Command Query Responsibility Segregation)** pattern:

- **Commands (`commands/`)**:
  - Encapsulate intent to mutate system or portfolio state (e.g. `DepositCashCommand`, `SubmitOrderCommand`, `RebalancePortfolioCommand`).
  - Represented by immutable `BaseCommand` value objects.
  - Handled by Use Cases that modify domain entities, execute policies, and save aggregate state via repositories.
- **Queries (`queries/`)**:
  - Encapsulate intent to read domain or analytics state without side-effects (e.g. `GetPortfolioSnapshotQuery`, `GetResearchReportQuery`).
  - Represented by immutable `BaseQuery` value objects.
  - Handled by Use Cases that retrieve data and map domain models into lightweight `BaseDTO` structures for presentation boundaries.

---

## 3. Architectural Dependency Direction

Clean Architecture mandates strict inward dependency flow:

```
[ UI / API / CLI ] ──► [ Application Layer ] ──► [ Core Domain Layer ]
                             │
                             ▼ (Defines Ports)
                     [ Outbound Ports ] ◄── (Implements Ports) ── [ Infrastructure ]
```

1. **Application → Domain**:
   - The application layer depends **ONLY** on the core domain layer (`packages.domain`).
   - Use cases instantiate domain value objects, invoke domain entities/services, and evaluate domain policies.
2. **Domain → Application**:
   - The core domain (`packages/domain/`) has **ZERO dependencies** on the application layer.
   - The domain remains completely unaware of CQRS commands, DTOs, or application use cases.
3. **Application → Infrastructure**:
   - The application layer defines abstract outbound port interfaces (`MarketDataPort`, `BrokerPort`, `LLMPort`, etc.) in `packages/application/ports/`.
   - The application layer **never** imports concrete databases, HTTP clients, web frameworks, or external SDKs.

---

## 4. Layer Responsibilities

- **`commands/`**: Immutable CQRS write command definitions derived from `BaseCommand`.
- **`queries/`**: Immutable CQRS read query definitions derived from `BaseQuery`.
- **`use_cases/`**: Single-responsibility workflow handlers derived from `BaseUseCase[TRequest, TResponse]`.
- **`dto/`**: Data Transfer Objects derived from `BaseDTO` for transferring serialized data across application boundaries.
- **`mappers/`**: Bi-directional mappers derived from `BaseMapper[TDomain, TDTO]` for transforming domain entities to/from DTOs.
- **`services/`**: Application services derived from `BaseApplicationService` for cross-cutting transaction and use-case workflow coordination.
- **`ports/`**: Abstract outbound port interfaces (`abc.ABC`) defining external driver requirements (`MarketDataPort`, `BrokerPort`, `ResearchPort`, `PortfolioPort`, `NotificationPort`, `LLMPort`, `StoragePort`).
- **`exceptions/`**: Application-level error classes derived from `ApplicationException`.

---

## 5. Why Infrastructure is Excluded

In accordance with Clean Architecture principles:

- **Framework Independence**: The application layer core does not depend on FastAPI, Flask, SQLAlchemy, Celery, or external HTTP libraries (`httpx`, `requests`).
- **Testability**: Use cases, mappers, commands, queries, and application services can be tested 100% in-memory using pure Python objects and mock/stub ports without setting up database connections, network mocks, or live API credentials.
- **Pluggable Technology**: Infrastructure details (e.g. PostgreSQL, Redis, DhanHQ/Shoonya broker APIs, Google GenAI SDK, S3 blob storage) can be swapped or upgraded without modifying a single line of business or application workflow code.
