"""
Execution Pipeline Abstraction.

Enforces human-in-the-loop trade execution workflow:
Recommendation -> User Approval -> Order Builder -> Risk Checks -> Zerodha Order API.
Never auto-places trades.
"""

import logging
from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from typing import Any

from packages.domain.brokerage.order import Order
from packages.domain.enums.trading import OrderStatus, OrderType, TradeType
from packages.domain.value_objects.core.price import Price
from packages.domain.value_objects.core.quantity import Quantity
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.domain.value_objects.identifiers.uuid_wrappers import BrokerId, OrderId, PortfolioId
from packages.infrastructure.brokers.zerodha import ZerodhaOrderManager

logger = logging.getLogger("ihf_ai.application.execution.execution_pipeline")


class ExecutionMode(StrEnum):
    """Trading execution mode."""

    PAPER = "PAPER"
    LIVE_ZERODHA = "LIVE_ZERODHA"


class ExecutionPipelineError(Exception):
    """Raised when execution pipeline validation or risk checks fail."""


@dataclass
class TradeRecommendation:
    """AI or strategy recommendation based on market data."""

    ticker: str
    action: str  # BUY or SELL
    target_quantity: float
    order_type: str = "LIMIT"
    suggested_price: float | None = None
    stop_loss_price: float | None = None
    reasoning: str = ""


@dataclass
class UserApprovalRequest:
    """Explicit human user approval context."""

    recommendation_id: str
    approved: bool
    approved_by_user_id: str
    override_quantity: float | None = None
    override_price: float | None = None
    product_type: str = "CNC"  # CNC, MIS, NRML
    execution_mode: ExecutionMode = ExecutionMode.LIVE_ZERODHA


class RiskCheckEngine:
    """Simple risk validation engine before routing orders to broker."""

    def __init__(
        self, max_order_value_inr: float = 500000.0, max_quantity: float = 10000.0
    ) -> None:
        self.max_order_value_inr = max_order_value_inr
        self.max_quantity = max_quantity

    def validate(self, order_params: dict[str, Any], available_margin: float | None = None) -> None:
        qty = float(order_params.get("quantity", 0))
        price = float(order_params.get("price", 0.0) or 0.0)
        est_val = qty * price if price > 0 else 0.0

        if qty <= 0:
            raise ExecutionPipelineError("Order quantity must be greater than zero.")
        if qty > self.max_quantity:
            raise ExecutionPipelineError(
                f"Order quantity {qty} exceeds maximum risk limit of {self.max_quantity}."
            )
        if est_val > self.max_order_value_inr:
            raise ExecutionPipelineError(
                f"Estimated order value ₹{est_val:.2f} exceeds maximum risk limit ₹{self.max_order_value_inr:.2f}."
            )
        if available_margin is not None and est_val > available_margin:
            raise ExecutionPipelineError(
                f"Required order value ₹{est_val:.2f} exceeds available margin ₹{available_margin:.2f}."
            )


class ExecutionPipeline:
    """
    Production Execution Pipeline enforcing:
    Recommendation -> User Approval -> Order Builder -> Risk Checks -> Zerodha Order API.
    """

    def __init__(
        self,
        zerodha_order_manager: ZerodhaOrderManager | Any | None = None,
        risk_engine: RiskCheckEngine | None = None,
        zerodha_order_service: Any | None = None,
    ) -> None:
        self.zerodha_order_manager = zerodha_order_manager or zerodha_order_service
        self.risk_engine = risk_engine or RiskCheckEngine()

    def process_execution(
        self,
        recommendation: TradeRecommendation,
        user_approval: UserApprovalRequest,
        portfolio_id: PortfolioId | str,
        broker_account_id: BrokerId | str,
        available_margin: float | None = None,
    ) -> Any:
        """
        Processes trade execution. Fails immediately if user approval is missing or unapproved.
        """
        # Step 1: User Approval Gate
        if not user_approval.approved:
            logger.warning("Execution rejected: Explicit user approval missing or declined.")
            raise ExecutionPipelineError("Execution blocked: Trade was not approved by user.")

        # Step 2: Order Builder
        final_quantity = user_approval.override_quantity or recommendation.target_quantity
        final_price = user_approval.override_price or recommendation.suggested_price
        product_type = user_approval.product_type

        order_params = {
            "ticker": recommendation.ticker,
            "action": recommendation.action,
            "quantity": final_quantity,
            "price": final_price,
            "order_type": recommendation.order_type,
            "product": product_type,
        }

        # Step 3: Risk Checks
        self.risk_engine.validate(order_params, available_margin=available_margin)

        if isinstance(portfolio_id, PortfolioId):
            pid = portfolio_id
        elif isinstance(portfolio_id, str):
            pid = PortfolioId.from_str(portfolio_id)
        else:
            pid = PortfolioId.generate()

        if isinstance(broker_account_id, BrokerId):
            bid = broker_account_id
        elif isinstance(broker_account_id, str):
            bid = BrokerId.from_str(broker_account_id)
        else:
            bid = BrokerId.generate()

        # Step 4: Route based on Execution Mode
        if user_approval.execution_mode == ExecutionMode.PAPER:
            logger.info("Routing order to PAPER trading engine for %s", recommendation.ticker)
            return Order(
                id=OrderId.generate(),
                portfolio_id=pid,
                broker_account_id=bid,
                ticker=Ticker(recommendation.ticker),
                order_type=OrderType(recommendation.order_type),
                trade_type=TradeType(recommendation.action.upper()),
                quantity=Quantity(Decimal(str(final_quantity))),
                price=Price.from_amount(final_price) if final_price else None,
                status=OrderStatus.FILLED,
            )

        if user_approval.execution_mode == ExecutionMode.LIVE_ZERODHA:
            if not self.zerodha_order_manager:
                raise ExecutionPipelineError(
                    "Zerodha order manager is not configured for LIVE execution."
                )

            logger.info("Routing approved trade to Zerodha Order API for %s", recommendation.ticker)
            res = self.zerodha_order_manager.place_order(
                {
                    "tradingsymbol": recommendation.ticker,
                    "transaction_type": recommendation.action,
                    "quantity": final_quantity,
                    "order_type": recommendation.order_type,
                    "product": product_type,
                    "price": float(final_price) if final_price else None,
                    "trigger_price": (
                        float(recommendation.stop_loss_price)
                        if recommendation.stop_loss_price
                        else None
                    ),
                }
            )
            if res is not None:
                return res

            return Order(
                id=OrderId.generate(),
                portfolio_id=pid,
                broker_account_id=bid,
                ticker=Ticker(recommendation.ticker),
                order_type=OrderType(recommendation.order_type),
                trade_type=TradeType(recommendation.action.upper()),
                quantity=Quantity(Decimal(str(final_quantity))),
                price=Price.from_amount(final_price) if final_price else None,
                status=OrderStatus.SUBMITTED,
            )

        raise ExecutionPipelineError(f"Unsupported execution mode: {user_approval.execution_mode}")
