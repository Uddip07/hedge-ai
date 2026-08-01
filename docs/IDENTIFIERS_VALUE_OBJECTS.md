# Identifier Value Objects Reference

This TDD documentation details the **Identifier Value Objects** implemented in `packages/domain/value_objects/identifiers/` for the **Indian AI Hedge Fund** platform.

Every value object is a frozen, immutable dataclass (`@dataclass(frozen=True, slots=True)`), self-validates upon construction, enforces structural invariants, implements dictionary serialization (`to_dict()`, `from_dict()`), and guarantees zero infrastructure dependencies.

---

## 1. Ticker (`packages/domain/value_objects/identifiers/ticker.py`)

Represents a stock, index, derivative, or commodity ticker symbol, bound optionally to an `ExchangeType` enum.

- **Attributes**: `symbol: str`, `exchange: Optional[ExchangeType] = None`
- **Validation**: Normalizes string via `validate_ticker_format`. Automatically parses exchange suffixes if present in input string (e.g. `'RELIANCE.NSE'` or `'INFY:NSE'`).
- **Properties**:
  - `full_symbol`: Canonical formatted string (e.g. `'RELIANCE.NSE'`).
  - `is_indian()`: Returns `True` if exchange is an Indian financial market (NSE, BSE, MCX).
- **Serialization**: `to_dict()`, `from_dict()`

---

## 2. ISIN (`packages/domain/value_objects/identifiers/isin.py`)

Represents an International Securities Identification Number (ISIN).

- **Attributes**: `value: str` (12-character uppercase string)
- **Validation**: Enforces 2-alpha country code prefix, 9-alphanumeric national ID, and final digit using the Luhn Modulus 10 double-add-double checksum algorithm (`validate_isin_checksum`).
- **Properties**:
  - `country_code`: 2-char prefix (e.g., `'IN'` for India).
  - `national_id`: 9-char payload.
  - `check_digit`: Final check digit.
  - `is_indian()`: Returns `True` if country code is `'IN'`.
- **Serialization**: `to_dict()`, `from_dict()`

---

## 3. Currency (`packages/domain/value_objects/identifiers/currency.py`)

Represents an ISO-4217 fiat currency wrapper around `CurrencyCode` enum.

- **Attributes**: `code: CurrencyCode` (default `CurrencyCode.INR`)
- **Properties**:
  - `symbol`: Currency symbol (e.g., `'₹'`, `'$'`).
  - `is_inr()`: Returns `True` for Indian Rupee.
- **Serialization**: `to_dict()`, `from_dict()`

---

## 4. Strongly-Typed UUID Wrappers (`packages/domain/value_objects/identifiers/uuid_wrappers.py`)

Prevents ID-mismatch bugs across bounded contexts by wrapping 128-bit UUID instances into distinct frozen value object types.

- **Base Class**: `EntityId(value: uuid.UUID)`
- **Derived Identifier Value Objects**:
  - `OrderId`
  - `TradeId`
  - `PortfolioId`
  - `ResearchId`
  - `StrategyId`
  - `BacktestId`
  - `BrokerId`
  - `UserId`
  - `PromptId`
  - `DocumentId`
  - `ExecutionId`
- **Methods**:
  - `.generate()`: Classmethod factory generating a random UUID v4 identifier.
  - `.from_str(val_str)`: Classmethod parsing string representations.
  - `to_dict()`, `from_dict()`: Serialization helpers.
