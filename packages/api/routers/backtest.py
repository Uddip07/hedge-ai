"""
FastAPI Router for Quantitative Backtesting Platform.

Exposes REST endpoints for triggering secured strategy backtest simulations,
tracking job runs, and retrieving persisted performance metrics and trade logs.
"""

import math
from datetime import UTC, date, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select

from packages.api.dependencies import verify_automation_key
from packages.infrastructure.database.models import (
    BacktestRunModel,
    BacktestTradeModel,
    CompanyModel,
    PriceHistoryDailyModel,
)
from packages.infrastructure.database.session import DatabaseManager
from packages.infrastructure.repositories.backtest_data_repository import SQLBacktestDataRepository

router = APIRouter(prefix="/api/v1/backtest", tags=["Quantitative Backtesting"])
db_manager = DatabaseManager()


class BacktestRunRequest(BaseModel):
    """Backtest simulation initiation request payload."""

    strategy_id: str = Field(default="MOMENTUM_SMA", description="Strategy identifier")
    symbols: list[str] = Field(
        default_factory=lambda: ["RELIANCE", "TCS"],
        description="Target ticker symbols",
    )
    start_date: date = Field(description="Simulation start date (YYYY-MM-DD)")
    end_date: date = Field(description="Simulation end date (YYYY-MM-DD)")
    initial_capital: float = Field(default=1000000.0, gt=0, description="Initial portfolio cash")
    parameters: dict[str, Any] = Field(default_factory=dict, description="Strategy parameters")


class BacktestTradeDTO(BaseModel):
    symbol: str
    action: str
    quantity: float
    price: float
    timestamp: str
    fees: float
    pnl: float | None = None


class BacktestRunResponse(BaseModel):
    """Backtest simulation execution result DTO."""

    run_id: str
    strategy_id: str
    symbols: list[str]
    start_date: date
    end_date: date
    initial_capital: float
    final_portfolio_value: float
    total_return_pct: float
    sharpe_ratio: float | None
    max_drawdown_pct: float | None
    total_trades: int
    trades: list[BacktestTradeDTO]
    status: str
    created_at: str


@router.post(
    "/run",
    response_model=BacktestRunResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(verify_automation_key)],
    summary="Trigger Quantitative Backtest Run",
    description="Execute backtest simulation on historical price series, compute performance metrics, and persist run details.",
)
def run_backtest(payload: BacktestRunRequest) -> BacktestRunResponse:
    """
    Execute deterministic point-in-time quantitative backtest for specified symbols.
    """
    if payload.start_date >= payload.end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date must be strictly before end_date.",
        )
    if not payload.symbols:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="symbols list cannot be empty.",
        )

    repo = SQLBacktestDataRepository(db_manager.session)
    executed_trades: list[BacktestTradeDTO] = []

    # Fetch daily price series for requested symbols
    with db_manager.session() as session:
        prices_by_symbol: dict[str, list[PriceHistoryDailyModel]] = {}
        for sym in payload.symbols:
            clean_sym = sym.strip().upper()
            stmt = (
                select(PriceHistoryDailyModel)
                .join(CompanyModel, PriceHistoryDailyModel.company_id == CompanyModel.id)
                .where(
                    CompanyModel.symbol == clean_sym,
                    PriceHistoryDailyModel.date >= payload.start_date,
                    PriceHistoryDailyModel.date <= payload.end_date,
                )
                .order_by(PriceHistoryDailyModel.date.asc())
            )
            rows = list(session.scalars(stmt).all())
            if rows:
                prices_by_symbol[clean_sym] = rows

    # Run multi-asset simulation
    current_cash = payload.initial_capital
    holdings: dict[str, float] = {s: 0.0 for s in payload.symbols}
    cost_basis: dict[str, float] = {s: 0.0 for s in payload.symbols}
    equity_curve: list[float] = [current_cash]

    # Collect all unique dates
    all_dates = sorted({p.date for plist in prices_by_symbol.values() for p in plist})

    final_val: float
    total_return: float
    sharpe: float | None
    max_dd: float | None

    if not all_dates:
        # If no DB prices found, calculate zero-activity baseline
        final_val = current_cash
        total_return = 0.0
        sharpe = None
        max_dd = 0.0
    else:
        # Simple quantitative momentum / SMA simulation logic
        sma_window = int(payload.parameters.get("sma_window", 10))
        allocation_per_symbol = current_cash / len(payload.symbols)

        for d in all_dates:
            day_equity = current_cash
            for sym, plist in prices_by_symbol.items():
                day_candle = next((p for p in plist if p.date == d), None)
                if not day_candle:
                    continue

                past_candles = [p for p in plist if p.date <= d]
                close_price = day_candle.close

                if len(past_candles) >= sma_window:
                    sma = sum(p.close for p in past_candles[-sma_window:]) / sma_window
                    curr_qty = holdings.get(sym, 0.0)

                    # Buy signal: Price crosses above SMA
                    if close_price > sma and curr_qty == 0:
                        buy_qty = math.floor(allocation_per_symbol / close_price)
                        if buy_qty > 0 and current_cash >= buy_qty * close_price:
                            trade_cost = buy_qty * close_price
                            fee = trade_cost * 0.0003  # 0.03% broker/STT fee
                            current_cash -= trade_cost + fee
                            holdings[sym] = buy_qty
                            cost_basis[sym] = close_price

                            executed_trades.append(
                                BacktestTradeDTO(
                                    symbol=sym,
                                    action="BUY",
                                    quantity=float(buy_qty),
                                    price=close_price,
                                    timestamp=datetime.combine(
                                        d, datetime.min.time(), tzinfo=UTC
                                    ).isoformat(),
                                    fees=round(fee, 2),
                                    pnl=0.0,
                                )
                            )

                    # Sell signal: Price crosses below SMA
                    elif close_price < sma and curr_qty > 0:
                        sell_qty = curr_qty
                        trade_proceeds = sell_qty * close_price
                        fee = trade_proceeds * 0.0003
                        pnl = (close_price - cost_basis[sym]) * sell_qty - fee
                        current_cash += trade_proceeds - fee
                        holdings[sym] = 0.0
                        cost_basis[sym] = 0.0

                        executed_trades.append(
                            BacktestTradeDTO(
                                symbol=sym,
                                action="SELL",
                                quantity=float(sell_qty),
                                price=close_price,
                                timestamp=datetime.combine(
                                    d, datetime.min.time(), tzinfo=UTC
                                ).isoformat(),
                                fees=round(fee, 2),
                                pnl=round(pnl, 2),
                            )
                        )

                # Add value of held assets
                day_equity += holdings.get(sym, 0.0) * close_price

            equity_curve.append(day_equity)

        # Liquidate remaining positions at final available close
        final_val = current_cash
        for sym, qty in holdings.items():
            if qty > 0 and sym in prices_by_symbol:
                final_close = prices_by_symbol[sym][-1].close
                final_val += qty * final_close

        total_return = round(
            ((final_val - payload.initial_capital) / payload.initial_capital) * 100.0, 2
        )

        # Compute Max Drawdown
        peak = equity_curve[0]
        max_dd = 0.0
        for val in equity_curve:
            if val > peak:
                peak = val
            dd = (peak - val) / peak if peak > 0 else 0.0
            if dd > max_dd:
                max_dd = dd
        max_dd = round(max_dd * 100.0, 2)

        # Compute Sharpe Ratio (Annualized, assuming 252 days)
        returns = []
        for i in range(1, len(equity_curve)):
            if equity_curve[i - 1] > 0:
                returns.append((equity_curve[i] - equity_curve[i - 1]) / equity_curve[i - 1])
        if returns and len(returns) > 1:
            mean_ret = sum(returns) / len(returns)
            variance = sum((r - mean_ret) ** 2 for r in returns) / (len(returns) - 1)
            std_dev = math.sqrt(variance) if variance > 0 else 0.0
            sharpe = round((mean_ret / std_dev) * math.sqrt(252), 2) if std_dev > 0 else None
        else:
            sharpe = None

    # Persist Backtest Run in database
    run_id = repo.save_run(
        strategy_name=payload.strategy_id,
        parameters=payload.parameters,
        start_date=payload.start_date,
        end_date=payload.end_date,
        initial_capital=payload.initial_capital,
        final_portfolio_value=final_val,
        total_return=total_return,
        sharpe_ratio=sharpe,
        max_drawdown=max_dd,
    )

    # Persist executed trades
    for t in executed_trades:
        repo.add_trade(
            run_id=run_id,
            symbol=t.symbol,
            action=t.action,
            quantity=t.quantity,
            price=t.price,
            timestamp=datetime.fromisoformat(t.timestamp),
            fees=t.fees,
            pnl=t.pnl,
        )

    return BacktestRunResponse(
        run_id=run_id,
        strategy_id=payload.strategy_id,
        symbols=payload.symbols,
        start_date=payload.start_date,
        end_date=payload.end_date,
        initial_capital=payload.initial_capital,
        final_portfolio_value=round(final_val, 2),
        total_return_pct=total_return,
        sharpe_ratio=sharpe,
        max_drawdown_pct=max_dd,
        total_trades=len(executed_trades),
        trades=executed_trades,
        status="COMPLETED",
        created_at=datetime.now(UTC).isoformat(),
    )


@router.get(
    "/{run_id}",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Get Backtest Run Details",
    description="Retrieve persisted backtest run results and associated trade executions.",
)
def get_backtest_run(run_id: str) -> dict[str, Any]:
    """Fetch backtest execution details and trades ledger by run_id."""
    with db_manager.session() as session:
        run = session.get(BacktestRunModel, run_id)
        if not run:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Backtest run '{run_id}' not found.",
            )

        trades_stmt = select(BacktestTradeModel).where(BacktestTradeModel.run_id == run_id)
        trades = list(session.scalars(trades_stmt).all())

        return {
            "run_id": run.id,
            "strategy_name": run.strategy_name,
            "parameters": run.parameters,
            "start_date": str(run.start_date),
            "end_date": str(run.end_date),
            "initial_capital": run.initial_capital,
            "final_portfolio_value": run.final_portfolio_value,
            "total_return_pct": run.total_return,
            "sharpe_ratio": run.sharpe_ratio,
            "max_drawdown_pct": run.max_drawdown,
            "created_at": run.created_at.isoformat(),
            "trades_count": len(trades),
            "trades": [
                {
                    "trade_id": t.id,
                    "symbol": t.symbol,
                    "action": t.action,
                    "quantity": t.quantity,
                    "price": t.price,
                    "timestamp": t.timestamp.isoformat(),
                    "fees": t.fees,
                    "pnl": t.pnl,
                }
                for t in trades
            ],
        }
