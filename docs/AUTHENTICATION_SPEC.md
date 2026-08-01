# MONEYYYYYY - Authentication & User Management Specification

## Overview

MONEYYYYYY provides an enterprise-grade, production-ready Authentication and User Management system built in compliance with Clean Architecture and Domain-Driven Design (DDD).

Every authenticated user owns:
1. **Paper Trading Account**: Dedicated paper trading portfolio automatically provisioned upon signup (default balance: 1,000,000 INR).
2. **Watchlist**: Personal list of tracked security tickers.
3. **Research History**: Historical records of stock analysis queries.
4. **Committee History**: Historical decisions from the Intelligent Investment Committee.
5. **Preferences**: Theme, currency, notifications, risk tolerance preferences.
6. **Settings**: Multi-Factor Authentication (MFA), session timeout, max active sessions, API access flags.

---

## Technical Security Architecture

### 1. Password Hashing
- **Algorithm**: Argon2id (`argon2-cffi` implementation)
- **Parameters**:
  - Time Cost: 2 iterations
  - Memory Cost: 64 MiB (65,536 KiB)
  - Parallelism: 2 threads
  - Salt Length: 16 bytes
  - Key Length: 32 bytes

### 2. Token Lifecycle & Management
- **Access Tokens**:
  - Format: JWT (JSON Web Token)
  - Signing Algorithm: HMAC-SHA256 (`HS256`)
  - Expiration: 15 minutes
  - Claims: `sub` (User ID), `role` (USER / ADMIN), `type` ("access"), `iat`, `exp`
- **Refresh Tokens**:
  - Format: Cryptographic JWT + Database Session Hash Tracking
  - Expiration: 7 days
  - Claims: `sub` (User ID), `sid` (Session UUID), `type` ("refresh"), `iat`, `exp`
  - Verification: Tokens are hashed using SHA-256 before session persistence for zero-leak security.

### 3. Role-Based Access Control (RBAC)
- Enforced via FastAPI dependencies (`get_current_user`, `require_role`).
- Supported Roles: `UserRole.USER`, `UserRole.ADMIN`.

### 4. Rate Limiting
- Auth endpoints (`/auth/signup`, `/auth/login`) feature IP-based sliding window rate limiting (10 requests / 60 seconds).

---

## API Endpoints Reference

| Method | Path | Auth Required | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/auth/signup` | Public | Register new user account & provision paper portfolio |
| `POST` | `/auth/login` | Public | Authenticate user & issue JWT Access + Refresh tokens |
| `POST` | `/auth/refresh` | Public | Refresh expired Access Token using valid Refresh Token |
| `POST` | `/auth/logout` | Protected | Invalidate active user session |
| `GET` | `/users/me` | Protected | Retrieve authenticated user profile & resource IDs |
| `PUT` | `/users/me` | Protected | Update profile metadata (e.g. full name) |
| `GET` | `/users/me/watchlist` | Protected | Retrieve user watchlist |
| `POST` | `/users/me/watchlist` | Protected | Add stock ticker to user watchlist |
| `DELETE` | `/users/me/watchlist/{symbol}` | Protected | Remove stock ticker from user watchlist |
| `PUT` | `/users/me/preferences` | Protected | Update user domain preferences |
| `PUT` | `/users/me/settings` | Protected | Update user operational settings |
| `GET` | `/users/admin/users` | Admin Only | List all registered platform users |
