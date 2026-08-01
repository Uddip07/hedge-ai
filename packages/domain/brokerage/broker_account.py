"""
BrokerAccount Aggregate Root for the Indian AI Hedge Fund Platform.

Root entity managing Orders, Executions, Brokerage Account Balances, and Margin Requirements.
Enforces order placement pre-checks, fill execution routing, and cash account balance invariants.
Pure domain entity with zero infrastructure dependencies.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from packages.domain.brokerage.balance import AccountBalance
from packages.domain.brokerage.execution import Execution
from packages.domain.brokerage.order import Order
from packages.domain.enums.system import BrokerType
from packages.domain.exceptions import EntityNotFoundError, InsufficientFundsError, ValidationError
from packages.domain.value_objects.core.money import Money
from packages.domain.value_objects.core.price import Price
from packages.domain.value_objects.core.quantity import Quantity
from packages.domain.value_objects.identifiers.uuid_wrappers import BrokerId, OrderId
from packages.domain.value_objects.temporal.timestamps import Timestamp


@dataclass
class BrokerAccount:
    """
    BrokerAccount Aggregate Root.

    Attributes:
        id (BrokerId): Unique broker account identifier.
        account_number (str): External broker account identification string.
        broker_type (BrokerType): Broker gateway connector type (DHAN, SHOONYA, ZERODHA, etc.).
        balance (AccountBalance): Current account cash and margin balance.
        orders (Dict[str, Order]): Tracked orders keyed by OrderId string.
        executions (List[Execution]): Execution fills ledger.
        created_at (Timestamp): Creation timestamp (UTC).
        updated_at (Timestamp): Last update timestamp (UTC).
    """

    account_number: str
    broker_type: BrokerType
    id: BrokerId = field(default_factory=BrokerId.generate)
    balance: AccountBalance = field(default_factory=lambda: AccountBalance(Money(Decimal("0.00"))))
    orders: dict[str, Order] = field(default_factory=dict)
    executions: list[Execution] = field(default_factory=list)
    created_at: Timestamp = field(default_factory=Timestamp.now_utc)
    updated_at: Timestamp = field(default_factory=Timestamp.now_utc)

    def __post_init__(self) -> None:
        if not isinstance(self.id, BrokerId):
            object.__setattr__(self, "id", BrokerId(self.id))
        if not isinstance(self.broker_type, BrokerType):
            object.__setattr__(self, "broker_type", BrokerType(self.broker_type))
        if not isinstance(self.balance, AccountBalance):
            object.__setattr__(self, "balance", AccountBalance(self.balance))
        if not isinstance(self.created_at, Timestamp):
            object.__setattr__(self, "created_at", Timestamp(self.created_at))
        if not isinstance(self.updated_at, Timestamp):
            object.__setattr__(self, "updated_at", Timestamp(self.updated_at))

        if not self.account_number.strip():
            raise ValidationError("Broker account_number cannot be empty.")

    def place_order(self, order: Order) -> Order:
        """
        Validate and record a new order placement.

        Raises:
            InsufficientFundsError: If BUY order value exceeds available buying power.
        """
        if order.trade_type.is_buy():
            est_price = order.price.amount if order.price else Decimal("0")
            est_value = Money(
                amount=est_price * order.quantity.value, currency=self.balance.currency
            )

            if est_value > self.balance.total_buying_power:
                raise InsufficientFundsError(
                    f"Insufficient buying power ({self.balance.total_buying_power}) for order value ({est_value}).",
                    context={
                        "required": str(est_value),
                        "available": str(self.balance.total_buying_power),
                    },
                )

        order_key = str(order.id)
        self.orders[order_key] = order
        self._touch()
        return order

    def cancel_order(self, order_id: OrderId) -> None:
        """
        Cancel an active order by ID.

        Raises:
            EntityNotFoundError: If order is not found in account.
        """
        order_key = str(order_id)
        if order_key not in self.orders:
            raise EntityNotFoundError(
                f"Order '{order_id}' not found in broker account '{self.account_number}'.",
                context={"account": self.account_number, "order_id": str(order_id)},
            )

        self.orders[order_key].cancel()
        self._touch()

    def execute_order_fill(
        self,
        order_id: OrderId,
        fill_quantity: Quantity,
        fill_price: Price,
        fee: Money | None = None,
        tax: Money | None = None,
        executed_at: Timestamp | None = None,
    ) -> Execution:
        """
        Record an order fill execution, updating order status and account cash balances.
        """
        order_key = str(order_id)
        if order_key not in self.orders:
            raise EntityNotFoundError(
                f"Order '{order_id}' not found in broker account '{self.account_number}'."
            )

        order = self.orders[order_key]
        execution = order.fill(
            fill_quantity=fill_quantity,
            fill_price=fill_price,
            fee=fee,
            tax=tax,
            executed_at=executed_at,
        )
        self.executions.append(execution)

        # Update account cash balance
        if order.trade_type.is_buy():
            new_cash = self.balance.available_cash - execution.net_amount
        else:
            new_cash = self.balance.available_cash + execution.net_amount

        self.balance = AccountBalance(
            available_cash=new_cash,
            used_margin=self.balance.used_margin,
            unrealized_pnl=self.balance.unrealized_pnl,
            currency=self.balance.currency,
        )

        self._touch()
        return execution

    def _touch(self) -> None:
        self.updated_at = Timestamp.now_utc()

    def to_dict(self) -> dict[str, Any]:
        """Serialize BrokerAccount Aggregate Root to dictionary."""
        return {
            "id": self.id.to_dict(),
            "account_number": self.account_number,
            "broker_type": self.broker_type.value,
            "balance": self.balance.to_dict(),
            "orders": {k: v.to_dict() for k, v in self.orders.items()},
            "executions": [e.to_dict() for e in self.executions],
            "created_at": self.created_at.to_dict(),
            "updated_at": self.updated_at.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BrokerAccount":
        """Deserialize dictionary to BrokerAccount Aggregate Root."""
        orders = {k: Order.from_dict(v) for k, v in data.get("orders", {}).items()}
        executions = [Execution.from_dict(e) for e in data.get("executions", [])]

        return cls(
            id=BrokerId.from_dict(data["id"]),
            account_number=data["account_number"],
            broker_type=BrokerType(data["broker_type"]),
            balance=AccountBalance.from_dict(data["balance"]),
            orders=orders,
            executions=executions,
            created_at=Timestamp.from_dict(data["created_at"]),
            updated_at=Timestamp.from_dict(data["updated_at"]),
        )

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, BrokerAccount):
            return self.id == other.id
        return False

    def __hash__(self) -> int:
        return hash(self.id)
