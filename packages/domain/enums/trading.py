"""
Trading Enums for the Indian AI Hedge Fund Domain.

Defines core asset categories, order types, order lifecycle statuses,
trade side indicators, position directions, and execution states.
"""

from enum import StrEnum


class AssetType(StrEnum):
    """
    Financial asset classes supported for research, backtesting, and live execution.
    Includes Indian specific asset vehicles like REITs and InvITs.
    """

    EQUITY = "EQUITY"
    ETF = "ETF"
    MUTUAL_FUND = "MUTUAL_FUND"
    INDEX = "INDEX"
    REIT = "REIT"
    INVIT = "INVIT"
    FUTURES = "FUTURES"
    OPTIONS = "OPTIONS"
    BOND = "BOND"
    COMMODITY = "COMMODITY"

    def is_derivative(self) -> bool:
        """Return True if the asset type is a derivative contract."""
        return self in {AssetType.FUTURES, AssetType.OPTIONS}

    def is_equity_like(self) -> bool:
        """Return True if the asset behaves like a spot equity instrument."""
        return self in {
            AssetType.EQUITY,
            AssetType.ETF,
            AssetType.REIT,
            AssetType.INVIT,
        }


class OrderType(StrEnum):
    """
    Order execution instructions for broker routing.
    Includes special Indian market order types (AMO, Cover, Bracket).
    """

    LIMIT = "LIMIT"
    MARKET = "MARKET"
    STOP_LOSS = "STOP_LOSS"
    STOP_LOSS_MARKET = "STOP_LOSS_MARKET"
    COVER = "COVER"
    BRACKET = "BRACKET"
    AMO = "AMO"
    ICEBERG = "ICEBERG"

    def requires_price(self) -> bool:
        """Return True if placing this order requires a limit price."""
        return self in {
            OrderType.LIMIT,
            OrderType.STOP_LOSS,
            OrderType.COVER,
            OrderType.BRACKET,
            OrderType.ICEBERG,
        }

    def is_advanced(self) -> bool:
        """Return True if the order type involves complex conditional logic."""
        return self in {
            OrderType.COVER,
            OrderType.BRACKET,
            OrderType.AMO,
            OrderType.ICEBERG,
        }


class OrderStatus(StrEnum):
    """
    Lifecycle status of a trading order.
    """

    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    TRIGGERED = "TRIGGERED"

    def is_active(self) -> bool:
        """Return True if the order is working and can still be filled or cancelled."""
        return self in {
            OrderStatus.PENDING,
            OrderStatus.SUBMITTED,
            OrderStatus.PARTIALLY_FILLED,
            OrderStatus.TRIGGERED,
        }

    def is_terminal(self) -> bool:
        """Return True if the order has completed its lifecycle."""
        return self in {
            OrderStatus.FILLED,
            OrderStatus.CANCELLED,
            OrderStatus.REJECTED,
            OrderStatus.EXPIRED,
        }

    def is_filled(self) -> bool:
        """Return True if the order has executed completely."""
        return self == OrderStatus.FILLED


class TradeType(StrEnum):
    """
    Direction of a trade execution (Buy / Sell).
    """

    BUY = "BUY"
    SELL = "SELL"

    def opposite(self) -> "TradeType":
        """Return the opposite trade side."""
        return TradeType.SELL if self == TradeType.BUY else TradeType.BUY

    def is_buy(self) -> bool:
        """Return True if this is a buy order/trade."""
        return self == TradeType.BUY

    def is_sell(self) -> bool:
        """Return True if this is a sell order/trade."""
        return self == TradeType.SELL


class PositionType(StrEnum):
    """
    Direction of an open portfolio position (Long / Short).
    """

    LONG = "LONG"
    SHORT = "SHORT"

    def opposite(self) -> "PositionType":
        """Return the opposite position direction."""
        return PositionType.SHORT if self == PositionType.LONG else PositionType.LONG

    def quantity_multiplier(self) -> int:
        """Return +1 for Long positions and -1 for Short positions."""
        return 1 if self == PositionType.LONG else -1


class ExecutionStatus(StrEnum):
    """
    Status of an execution gateway routing task.
    """

    QUEUED = "QUEUED"
    ROUTED = "ROUTED"
    EXECUTING = "EXECUTING"
    EXECUTED = "EXECUTED"
    PARTIALLY_EXECUTED = "PARTIALLY_EXECUTED"
    FAILED = "FAILED"
    REJECTED = "REJECTED"

    def is_successful(self) -> bool:
        """Return True if execution completed successfully."""
        return self in {ExecutionStatus.EXECUTED, ExecutionStatus.PARTIALLY_EXECUTED}

    def is_terminal(self) -> bool:
        """Return True if execution attempt has finished."""
        return self in {
            ExecutionStatus.EXECUTED,
            ExecutionStatus.FAILED,
            ExecutionStatus.REJECTED,
        }


class ProductType(StrEnum):
    """
    Broker product / margin leverage instruction type for order execution in Indian markets.
    """

    CNC = "CNC"  # Cash and Carry (Delivery equity)
    MIS = "MIS"  # Margin Intraday Squareoff (Intraday leverage)
    NRML = "NRML"  # Normal (F&O / Overnight position)

    def is_intraday(self) -> bool:
        """Return True if this product type is intraday only."""
        return self == ProductType.MIS

    def is_delivery(self) -> bool:
        """Return True if this product type is delivery equity."""
        return self == ProductType.CNC
