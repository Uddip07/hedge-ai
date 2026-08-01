"""
Portfolio Aggregate Root for the Indian AI Hedge Fund Platform.

Central domain aggregate root managing holdings, active positions, trade executions,
cash balance, and historical performance snapshots. Pure domain aggregate root.
"""

import uuid
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from packages.domain.enums.portfolio import PortfolioType
from packages.domain.enums.trading import PositionType, TradeType
from packages.domain.exceptions.portfolio import InsufficientFundsError, PortfolioError
from packages.domain.exceptions.validation import ValidationError
from packages.domain.portfolio.holding import Holding
from packages.domain.portfolio.position import Position
from packages.domain.portfolio.snapshot import PortfolioSnapshot
from packages.domain.portfolio.trade import Trade
from packages.domain.value_objects.core.money import Money
from packages.domain.value_objects.core.price import Price
from packages.domain.value_objects.identifiers import PortfolioId, Ticker
from packages.domain.value_objects.temporal.timestamps import Timestamp


@dataclass
class Portfolio:
    """
    Aggregate Root representing an investment portfolio (Live, Paper, or Backtest).

    Enforces invariants across holdings, cash balances, trades, and position tracking.
    """

    name: str
    portfolio_type: PortfolioType
    id: PortfolioId = field(default_factory=PortfolioId.generate)
    cash_balance: Money = field(default_factory=lambda: Money(Decimal("0.00")))
    holdings: dict[str, Holding] = field(default_factory=dict)
    positions: list[Position] = field(default_factory=list)
    trades: list[Trade] = field(default_factory=list)
    snapshots: list[PortfolioSnapshot] = field(default_factory=list)
    owner_id: uuid.UUID | None = None
    created_at: Timestamp = field(default_factory=Timestamp.now_utc)
    updated_at: Timestamp = field(default_factory=Timestamp.now_utc)

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValidationError("Portfolio name cannot be empty.")
        if not isinstance(self.portfolio_type, PortfolioType):
            self.portfolio_type = PortfolioType(self.portfolio_type)

    def deposit_cash(self, amount: Money) -> Money:
        """
        Deposit cash into portfolio balance.

        Returns:
            Money: Updated total cash balance.
        """
        if amount.amount <= Decimal("0"):
            raise ValidationError("Deposit amount must be strictly positive.")
        self.cash_balance = self.cash_balance + amount
        self._touch()
        return self.cash_balance

    def withdraw_cash(self, amount: Money) -> Money:
        """
        Withdraw cash from portfolio balance.

        Raises:
            InsufficientFundsError: If withdrawal exceeds available cash.
        """
        if amount.amount <= Decimal("0"):
            raise ValidationError("Withdrawal amount must be strictly positive.")
        if self.cash_balance < amount:
            raise InsufficientFundsError(
                f"Insufficient funds for withdrawal of {amount}. Current cash: {self.cash_balance}.",
                context={
                    "requested": str(amount),
                    "available": str(self.cash_balance),
                },
            )
        self.cash_balance = self.cash_balance - amount
        self._touch()
        return self.cash_balance

    def update_holding_price(self, ticker: Ticker, price: Price) -> None:
        """Update current market price for a holding symbol."""
        sym = ticker.full_symbol if hasattr(ticker, "full_symbol") else str(ticker)
        if sym in self.holdings:
            self.holdings[sym].update_price(price)
            self._touch()

    def total_equity(self) -> Money:
        """Calculate total portfolio equity (cash balance + market value of holdings)."""
        holdings_val = sum(
            (h.current_value.amount for h in self.holdings.values()), Decimal("0.00")
        )
        total_amt = self.cash_balance.amount + holdings_val
        return Money(total_amt, currency=self.cash_balance.currency)

    def total_invested_capital(self) -> Money:
        """Calculate total market value of current open holdings."""
        invested_amt = sum(
            (h.current_value.amount for h in self.holdings.values()), Decimal("0.00")
        )
        return Money(invested_amt, currency=self.cash_balance.currency)

    def total_unrealized_pnl(self) -> Money:
        """Calculate aggregate unrealized PnL across all open holdings."""
        pnl_amt = sum((h.unrealized_pnl.amount for h in self.holdings.values()), Decimal("0.00"))
        return Money(pnl_amt, currency=self.cash_balance.currency)

    def total_realized_pnl(self) -> Money:
        """Calculate aggregate realized PnL across all executed trades."""
        pnl_amt = sum(
            (t.net_amount.amount for t in self.trades if t.is_closing_trade),
            Decimal("0.00"),
        )
        return Money(pnl_amt, currency=self.cash_balance.currency)

    def record_trade(self, trade: Trade) -> None:
        """Alias for execute_trade."""
        self.execute_trade(trade)

    def execute_trade(self, trade: Trade) -> None:
        """
        Process an executed trade, updating cash, holdings, and position state.

        Raises:
            InsufficientFundsError: If BUY trade exceeds available cash.
        """
        symbol_key = trade.ticker.full_symbol

        if trade.trade_type == TradeType.BUY:
            total_cost = trade.gross_amount + trade.fees
            if self.cash_balance < total_cost:
                raise InsufficientFundsError(
                    f"Insufficient funds for BUY trade {trade.ticker.symbol}. Required {total_cost}, available {self.cash_balance}.",
                    context={
                        "required": str(total_cost),
                        "available": str(self.cash_balance),
                    },
                )

            # Deduct cash
            self.cash_balance = self.cash_balance - total_cost

            # Update or create holding
            if symbol_key in self.holdings:
                self.holdings[symbol_key] = self.holdings[symbol_key].add_quantity(
                    trade.quantity, trade.price
                )
            else:
                self.holdings[symbol_key] = Holding(
                    ticker=trade.ticker,
                    quantity=trade.quantity,
                    average_buy_price=trade.price,
                    current_price=trade.price,
                )

            # Add or update open position
            open_pos = next(
                (p for p in self.positions if p.is_open and p.ticker.full_symbol == symbol_key),
                None,
            )
            if open_pos:
                open_pos.add_execution(trade.quantity, trade.price)
            else:
                new_pos = Position(
                    ticker=trade.ticker,
                    position_type=PositionType.LONG,
                    quantity=trade.quantity,
                    entry_price=trade.price,
                    opened_at=trade.executed_at,
                    portfolio_id=self.id,
                )
                self.positions.append(new_pos)

        elif trade.trade_type == TradeType.SELL:
            if (
                symbol_key not in self.holdings
                or self.holdings[symbol_key].quantity < trade.quantity
            ):
                raise PortfolioError(
                    f"Cannot execute SELL for {trade.ticker.symbol}. Insufficient holding quantity.",
                    context={"symbol": symbol_key, "requested": str(trade.quantity)},
                )

            net_proceeds = trade.gross_amount - trade.fees
            self.cash_balance = self.cash_balance + net_proceeds

            # Reduce or remove holding
            new_holding = self.holdings[symbol_key].reduce_quantity(trade.quantity)
            if new_holding is None or new_holding.quantity.value == Decimal("0"):
                del self.holdings[symbol_key]
            else:
                self.holdings[symbol_key] = new_holding

            # Close matching open Long position if exists
            for pos in self.positions:
                if pos.is_open and pos.ticker.full_symbol == symbol_key:
                    pos.close_position(trade.price, trade.executed_at)
                    break

        self.trades.append(trade)
        self._touch()

    def create_snapshot(self, ts: Timestamp | None = None) -> PortfolioSnapshot:
        """Create and store a point-in-time PortfolioSnapshot."""
        snapshot_time = ts or Timestamp.now_utc()
        snapshot = PortfolioSnapshot(
            portfolio_id=self.id.value,
            timestamp=snapshot_time,
            total_equity=self.total_equity(),
            cash_balance=self.cash_balance,
            invested_capital=self.total_invested_capital(),
            unrealized_pnl=self.total_unrealized_pnl(),
            realized_pnl=self.total_realized_pnl(),
            holding_count=len(self.holdings),
        )
        self.snapshots.append(snapshot)
        self._touch()
        return snapshot

    def _touch(self) -> None:
        self.updated_at = Timestamp.now_utc()

    def to_dict(self) -> dict[str, Any]:
        """Serialize Portfolio aggregate root to dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "portfolio_type": self.portfolio_type.value,
            "cash_balance": self.cash_balance.to_dict(),
            "holdings": {k: v.to_dict() for k, v in self.holdings.items()},
            "positions": [p.to_dict() for p in self.positions],
            "trades": [t.to_dict() for t in self.trades],
            "snapshots": [s.to_dict() for s in self.snapshots],
            "owner_id": str(self.owner_id) if self.owner_id else None,
            "created_at": self.created_at.iso_format,
            "updated_at": self.updated_at.iso_format,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Portfolio":
        """Deserialize dictionary to Portfolio aggregate root."""
        holdings = {k: Holding.from_dict(v) for k, v in data.get("holdings", {}).items()}
        positions = [Position.from_dict(p) for p in data.get("positions", [])]
        trades = [Trade.from_dict(t) for t in data.get("trades", [])]
        snapshots = [PortfolioSnapshot.from_dict(s) for s in data.get("snapshots", [])]

        return cls(
            id=PortfolioId.from_dict(data["id"]),
            name=data["name"],
            portfolio_type=PortfolioType(data["portfolio_type"]),
            cash_balance=Money.from_dict(data["cash_balance"]),
            holdings=holdings,
            positions=positions,
            trades=trades,
            snapshots=snapshots,
            owner_id=uuid.UUID(data["owner_id"]) if data.get("owner_id") else None,
            created_at=Timestamp.from_iso(data["created_at"]),
            updated_at=Timestamp.from_iso(data["updated_at"]),
        )
