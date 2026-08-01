"""
SQL Backtest Data Repository Implementation.

Persists backtest runs, executed trades, and performance strategy results.
"""

import uuid
from datetime import UTC, date, datetime
from typing import Any

from packages.infrastructure.database.models import (
    BacktestRunModel,
    BacktestTradeModel,
)


class SQLBacktestDataRepository:
    """
    Repository for persisting backtesting runs and trade execution records.
    """

    def __init__(self, session_factory: Any) -> None:
        self.session_factory = session_factory

    def save_run(
        self,
        strategy_name: str,
        parameters: dict[str, Any],
        start_date: date,
        end_date: date,
        initial_capital: float,
        final_portfolio_value: float,
        total_return: float,
        sharpe_ratio: float | None = None,
        max_drawdown: float | None = None,
    ) -> str:
        """Create and persist a new BacktestRunModel."""
        run_id = str(uuid.uuid4())
        with self.session_factory() as session:
            run = BacktestRunModel(
                id=run_id,
                strategy_name=strategy_name,
                parameters=parameters,
                start_date=start_date,
                end_date=end_date,
                initial_capital=initial_capital,
                final_portfolio_value=final_portfolio_value,
                total_return=total_return,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                created_at=datetime.now(UTC),
            )
            session.add(run)
            session.commit()
        return run_id

    def add_trade(
        self,
        run_id: str,
        symbol: str,
        action: str,
        quantity: float,
        price: float,
        timestamp: datetime,
        company_id: str | None = None,
        fees: float = 0.0,
        pnl: float | None = None,
    ) -> str:
        """Add individual executed trade to backtest run."""
        trade_id = str(uuid.uuid4())
        with self.session_factory() as session:
            trade = BacktestTradeModel(
                id=trade_id,
                run_id=run_id,
                company_id=company_id,
                symbol=symbol.upper(),
                action=action.upper(),
                quantity=quantity,
                price=price,
                timestamp=timestamp,
                fees=fees,
                pnl=pnl,
            )
            session.add(trade)
            session.commit()
        return trade_id

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        """Retrieve full details of a backtest run."""
        with self.session_factory() as session:
            run = session.get(BacktestRunModel, run_id)
            if not run:
                return None
            return {
                "id": run.id,
                "strategy_name": run.strategy_name,
                "parameters": run.parameters,
                "start_date": run.start_date,
                "end_date": run.end_date,
                "initial_capital": run.initial_capital,
                "final_portfolio_value": run.final_portfolio_value,
                "total_return": run.total_return,
                "sharpe_ratio": run.sharpe_ratio,
                "max_drawdown": run.max_drawdown,
                "created_at": run.created_at,
            }
