# Backend Developer Onboarding & Architecture Guide

## 1. Welcome to MONEYYYYYY
MONEYYYYYY is a production-grade AI Investment Operating System designed specifically for institutional asset management and Indian equity markets (NSE, BSE).

---

## 2. Core Architectural Principles
- **Clean Architecture & DDD**: Strict layer isolation.
- **SOLID**: Single Responsibility, Open-Closed, Liskov Substitution, Interface Segregation, Dependency Inversion.
- **Provider Abstraction**: Infrastructure providers (OpenBB, NSE, Yahoo) are plugins behind ports.
- **Zero Mocking in Production**: `ENV=production` strictly enforces production data providers.

---

## 3. Development Workflow
1. Environment configuration (`.env`).
2. Run test suite (`python -m unittest discover tests`).
3. Run static type checking (`python -m mypy packages/...`).
4. Run linting (`python -m ruff check .`).
5. Run formatting (`python -m black .`).
