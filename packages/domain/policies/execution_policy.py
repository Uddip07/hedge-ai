"""
ExecutionPolicy Domain Specification for the Indian AI Hedge Fund Platform.

Encapsulates trade execution rules (market session state, lot size alignment,
tick size alignment, limit price collar validation). Pure domain policy.
"""

from dataclasses import dataclass
from decimal import Decimal

from packages.domain.brokerage.order import Order
from packages.domain.enums.market import MarketSession
from packages.domain.exceptions import ValidationError
from packages.domain.market.asset import Asset
from packages.domain.value_objects.core.price import Price


@dataclass(frozen=True, slots=True)
class ExecutionPolicy:
    """
    Immutable domain policy enforcing order execution pre-checks.

    Attributes:
        allowed_sessions (Tuple[MarketSession, ...]): Market sessions where orders can be routed.
        max_price_collar_pct (Decimal): Maximum allowed limit order price deviation from reference price (default 5%).
    """

    allowed_sessions: tuple[MarketSession, ...] = (MarketSession.NORMAL, MarketSession.PRE_MARKET)
    max_price_collar_pct: Decimal = Decimal("5.0")

    def validate_execution_rules(
        self,
        asset: Asset,
        order: Order,
        current_session: MarketSession,
        reference_price: Price | None = None,
    ) -> tuple[bool, list[str]]:
        """
        Validate whether an order meets operational market execution rules.

        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_policy_violations)
        """
        violations: list[str] = []

        # 1. Market session check
        if current_session not in self.allowed_sessions:
            violations.append(
                f"Market session '{current_session.value}' does not allow order execution."
            )

        # 2. Lot size alignment check
        try:
            asset.validate_order_quantity(order.quantity)
        except ValidationError as exc:
            violations.append(str(exc))

        # 3. Tick size alignment check
        if order.price:
            try:
                asset.validate_order_price(order.price)
            except ValidationError as exc:
                violations.append(str(exc))

        # 4. Limit price collar check
        if order.price and reference_price:
            dev_pct = (
                abs(order.price.amount - reference_price.amount) / reference_price.amount
            ) * Decimal("100")
            if dev_pct > self.max_price_collar_pct:
                violations.append(
                    f"Limit order price ({order.price.amount}) deviates {dev_pct:.2f}% from reference price "
                    f"({reference_price.amount}), exceeding price collar limit ({self.max_price_collar_pct}%)."
                )

        return len(violations) == 0, violations
