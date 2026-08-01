"""
SQLAlchemy 2.x Database Models for Infrastructure Persistence.
"""

import uuid
from datetime import UTC, date, datetime
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from packages.infrastructure.database.session import Base


class UserModel(Base):
    """
    SQLAlchemy ORM Model for User Aggregate Root.
    """

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="USER")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    paper_portfolio_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    watchlist: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    research_history: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    committee_history: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    preferences: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    settings: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )


class UserSessionModel(Base):
    """
    SQLAlchemy ORM Model for UserSession.
    """

    __tablename__ = "user_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    refresh_token_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    user_agent: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    ip_address: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    is_revoked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )


class CompanyModel(Base):
    """
    SQLAlchemy ORM Model for Companies.
    """

    __tablename__ = "companies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    exchange: Mapped[str] = mapped_column(String(20), nullable=False, default="NSE", index=True)
    sector: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    isin: Mapped[str | None] = mapped_column(String(20), nullable=True, unique=True)
    market_cap_category: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # Large Cap, Mid Cap, Small Cap
    listing_status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")
    index_membership: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

    prices: Mapped[list["PriceHistoryDailyModel"]] = relationship(
        "PriceHistoryDailyModel", back_populates="company"
    )


class SymbolModel(Base):
    """
    SQLAlchemy ORM Model for Symbols/Tickers lookup.
    """

    __tablename__ = "symbols"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    exchange: Mapped[str] = mapped_column(String(20), nullable=False, default="NSE", index=True)
    asset_type: Mapped[str] = mapped_column(String(30), nullable=False, default="EQUITY")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )


class PriceHistoryDailyModel(Base):
    """
    SQLAlchemy ORM Model for Daily/Intraday Historical Price Records.
    """

    __tablename__ = "price_history_daily"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    open: Mapped[float] = mapped_column(Float, nullable=False)
    high: Mapped[float] = mapped_column(Float, nullable=False)
    low: Mapped[float] = mapped_column(Float, nullable=False)
    close: Mapped[float] = mapped_column(Float, nullable=False)
    adjusted_close: Mapped[float | None] = mapped_column(Float, nullable=True)
    volume: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    vwap: Mapped[float | None] = mapped_column(Float, nullable=True)
    delivery_quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    turnover: Mapped[float | None] = mapped_column(Float, nullable=True)

    company: Mapped["CompanyModel"] = relationship("CompanyModel", back_populates="prices")

    __table_args__ = (
        UniqueConstraint("company_id", "date", name="uq_price_history_company_date"),
        Index("idx_price_history_company_date", "company_id", "date"),
    )


class MarketIndexModel(Base):
    """
    SQLAlchemy ORM Model for Market Index Data (e.g. NIFTY50, BANKNIFTY).
    """

    __tablename__ = "market_indices"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    open: Mapped[float] = mapped_column(Float, nullable=False)
    high: Mapped[float] = mapped_column(Float, nullable=False)
    low: Mapped[float] = mapped_column(Float, nullable=False)
    close: Mapped[float] = mapped_column(Float, nullable=False)
    volume: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    change: Mapped[float | None] = mapped_column(Float, nullable=True)
    pct_change: Mapped[float | None] = mapped_column(Float, nullable=True)

    __table_args__ = (
        UniqueConstraint("symbol", "date", name="uq_market_index_symbol_date"),
        Index("idx_market_index_symbol_date", "symbol", "date"),
    )


class CorporateActionModel(Base):
    """
    SQLAlchemy ORM Model for Corporate Actions (Bonus, Rights Issue, Buyback, etc.).
    """

    __tablename__ = "corporate_actions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    ex_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    record_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    ratio_value: Mapped[str | None] = mapped_column(String(50), nullable=True)


class DividendModel(Base):
    """
    SQLAlchemy ORM Model for Dividend History.
    """

    __tablename__ = "dividends"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    ex_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    dividend_amount: Mapped[float] = mapped_column(Float, nullable=False)
    dividend_type: Mapped[str] = mapped_column(String(30), nullable=False, default="INTERIM")
    payment_date: Mapped[date | None] = mapped_column(Date, nullable=True)


class SplitModel(Base):
    """
    SQLAlchemy ORM Model for Stock Splits.
    """

    __tablename__ = "splits"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    ex_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    split_factor: Mapped[float] = mapped_column(Float, nullable=False)
    from_shares: Mapped[int] = mapped_column(Integer, nullable=False)
    to_shares: Mapped[int] = mapped_column(Integer, nullable=False)


class MarketCalendarModel(Base):
    """
    SQLAlchemy ORM Model for Exchange Trading Days and Holidays.
    """

    __tablename__ = "market_calendar"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    date: Mapped[date] = mapped_column(Date, unique=True, nullable=False, index=True)
    is_trading_day: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    exchange: Mapped[str] = mapped_column(String(20), nullable=False, default="NSE")
    market_open_time: Mapped[str] = mapped_column(String(10), nullable=False, default="09:15:00")
    market_close_time: Mapped[str] = mapped_column(String(10), nullable=False, default="15:30:00")
    holiday_name: Mapped[str | None] = mapped_column(String(100), nullable=True)


class FeatureCacheModel(Base):
    """
    SQLAlchemy ORM Model for Engine Feature Cache (Calculated Technical Indicators).
    """

    __tablename__ = "feature_cache"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    feature_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    feature_value: Mapped[float] = mapped_column(Float, nullable=False)
    feature_version: Mapped[str] = mapped_column(String(20), nullable=False, default="v1.0")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

    __table_args__ = (
        UniqueConstraint(
            "company_id", "date", "feature_name", "feature_version", name="uq_feature_cache_record"
        ),
        Index("idx_feature_cache_lookup", "company_id", "date", "feature_name"),
    )


class ImportJobModel(Base):
    """
    SQLAlchemy ORM Model for Bulk Import Engine Job Tracking.
    """

    __tablename__ = "import_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="PENDING", index=True)
    target_directory: Mapped[str] = mapped_column(String(500), nullable=False)
    total_files: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    processed_files: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    logs: Mapped[list["ImportLogModel"]] = relationship("ImportLogModel", back_populates="job")


class ImportLogModel(Base):
    """
    SQLAlchemy ORM Model for Per-File Import Execution Log.
    """

    __tablename__ = "import_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("import_jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="PENDING")
    rows_imported: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rows_skipped: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_details: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

    job: Mapped["ImportJobModel"] = relationship("ImportJobModel", back_populates="logs")


class BacktestRunModel(Base):
    """
    SQLAlchemy ORM Model for Backtest Execution Records.
    """

    __tablename__ = "backtest_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    strategy_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    parameters: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    initial_capital: Mapped[float] = mapped_column(Float, nullable=False)
    final_portfolio_value: Mapped[float] = mapped_column(Float, nullable=False)
    total_return: Mapped[float] = mapped_column(Float, nullable=False)
    sharpe_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_drawdown: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

    trades: Mapped[list["BacktestTradeModel"]] = relationship(
        "BacktestTradeModel", back_populates="run"
    )
    results: Mapped[list["StrategyResultModel"]] = relationship(
        "StrategyResultModel", back_populates="run"
    )


class BacktestTradeModel(Base):
    """
    SQLAlchemy ORM Model for Individual Trades Executed in Backtests.
    """

    __tablename__ = "backtest_trades"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("backtest_runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    company_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    symbol: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(10), nullable=False)  # BUY, SELL
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fees: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    pnl: Mapped[float | None] = mapped_column(Float, nullable=True)

    run: Mapped["BacktestRunModel"] = relationship("BacktestRunModel", back_populates="trades")


class StrategyResultModel(Base):
    """
    SQLAlchemy ORM Model for Strategy Performance Metrics.
    """

    __tablename__ = "strategy_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("backtest_runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False)
    metric_value: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

    run: Mapped["BacktestRunModel"] = relationship("BacktestRunModel", back_populates="results")


class SystemMetadataModel(Base):
    """
    SQLAlchemy ORM Model for System Configuration and Metadata Key-Values.
    """

    __tablename__ = "system_metadata"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
