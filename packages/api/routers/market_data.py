"""
FastAPI Router for Historical Market Data Platform.

Exposes REST API endpoints for data import, job tracking, database statistics,
symbol/company lookups, historical prices, market replay, and backtesting feeds.
"""

from datetime import date
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func, select

from packages.infrastructure.database.config import DatabaseConfig
from packages.infrastructure.database.models import (
    CompanyModel,
    ImportJobModel,
    PriceHistoryDailyModel,
    SymbolModel,
)
from packages.infrastructure.database.session import DatabaseManager
from packages.infrastructure.market_data.importer import MarketDataImporter
from packages.infrastructure.market_data.replay import MarketReplayService
from packages.infrastructure.market_data.scanner import DataScanner

router = APIRouter(prefix="/api/v1/market-data", tags=["Market Data Platform"])
db_manager = DatabaseManager()


# Response Schemas
class CompanyResponse(BaseModel):
    id: str
    symbol: str
    company_name: str
    exchange: str
    sector: str | None = None
    industry: str | None = None
    isin: str | None = None
    market_cap_category: str | None = None
    listing_status: str


class PriceHistoryResponse(BaseModel):
    date: date
    open: float
    high: float
    low: float
    close: float
    adjusted_close: float | None = None
    volume: int
    vwap: float | None = None


class DatabaseStatsResponse(BaseModel):
    total_companies: int
    total_symbols: int
    total_price_records: int
    total_import_jobs: int
    database_url: str
    market_data_path: str


class ImportTriggerResponse(BaseModel):
    job_id: str
    status: str
    target_directory: str
    message: str


@router.get("/stats", response_model=DatabaseStatsResponse)
def get_database_stats() -> DatabaseStatsResponse:
    """Retrieve historical market data platform statistics."""
    with db_manager.session() as session:
        companies_count = session.scalar(select(func.count(CompanyModel.id))) or 0
        symbols_count = session.scalar(select(func.count(SymbolModel.id))) or 0
        prices_count = session.scalar(select(func.count(PriceHistoryDailyModel.id))) or 0
        jobs_count = session.scalar(select(func.count(ImportJobModel.id))) or 0

        cfg = DatabaseConfig()

        return DatabaseStatsResponse(
            total_companies=companies_count,
            total_symbols=symbols_count,
            total_price_records=prices_count,
            total_import_jobs=jobs_count,
            database_url=cfg.url.split("@")[-1] if "@" in cfg.url else cfg.url,
            market_data_path=cfg.market_data_path,
        )


@router.get("/symbols")
def list_symbols() -> list[dict[str, Any]]:
    """List all registered trading symbols."""
    with db_manager.session() as session:
        rows = session.scalars(select(SymbolModel).order_by(SymbolModel.symbol.asc())).all()
        return [
            {
                "id": r.id,
                "symbol": r.symbol,
                "name": r.name,
                "exchange": r.exchange,
                "asset_type": r.asset_type,
                "is_active": r.is_active,
            }
            for r in rows
        ]


@router.get("/companies/{symbol}", response_model=CompanyResponse)
def get_company(symbol: str) -> CompanyResponse:
    """Fetch company information by ticker symbol."""
    clean_sym = symbol.strip().upper()
    with db_manager.session() as session:
        comp = session.scalar(select(CompanyModel).where(CompanyModel.symbol == clean_sym))
        if not comp:
            raise HTTPException(status_code=404, detail=f"Company symbol '{clean_sym}' not found")
        return CompanyResponse(
            id=comp.id,
            symbol=comp.symbol,
            company_name=comp.company_name,
            exchange=comp.exchange,
            sector=comp.sector,
            industry=comp.industry,
            isin=comp.isin,
            market_cap_category=comp.market_cap_category,
            listing_status=comp.listing_status,
        )


@router.get("/prices/{symbol}", response_model=list[PriceHistoryResponse])
def get_prices(
    symbol: str,
    start_date: date | None = None,
    end_date: date | None = None,
    limit: int = Query(default=1000, le=10000),
) -> list[PriceHistoryResponse]:
    """Fetch historical daily price series for a company."""
    clean_sym = symbol.strip().upper()
    with db_manager.session() as session:
        stmt = (
            select(PriceHistoryDailyModel)
            .join(CompanyModel, PriceHistoryDailyModel.company_id == CompanyModel.id)
            .where(CompanyModel.symbol == clean_sym)
        )
        if start_date:
            stmt = stmt.where(PriceHistoryDailyModel.date >= start_date)
        if end_date:
            stmt = stmt.where(PriceHistoryDailyModel.date <= end_date)

        stmt = stmt.order_by(PriceHistoryDailyModel.date.asc()).limit(limit)
        rows = session.scalars(stmt).all()

        return [
            PriceHistoryResponse(
                date=r.date,
                open=r.open,
                high=r.high,
                low=r.low,
                close=r.close,
                adjusted_close=r.adjusted_close,
                volume=r.volume,
                vwap=r.vwap,
            )
            for r in rows
        ]


@router.post("/import", response_model=ImportTriggerResponse)
def trigger_import(path: str | None = None) -> ImportTriggerResponse:
    """Trigger background bulk dataset import scan and ingestion."""
    cfg = DatabaseConfig()
    target_path = Path(path or cfg.market_data_path)

    scanner = DataScanner(target_path)
    discovered_files = scanner.scan_files()

    if not discovered_files:
        return ImportTriggerResponse(
            job_id="",
            status="SKIPPED",
            target_directory=str(target_path),
            message=f"No supported CSV/Zip files found under '{target_path}'",
        )

    importer = MarketDataImporter(db_manager.session, batch_size=5000)
    stats = importer.import_discovered_files(discovered_files, str(target_path))

    return ImportTriggerResponse(
        job_id=stats.job_id,
        status=stats.status,
        target_directory=str(target_path),
        message=f"Import complete. Processed {stats.files_processed} files, imported {stats.rows_imported} rows.",
    )


@router.get("/import/status")
def import_status() -> list[dict[str, Any]]:
    """List recent import job execution statuses."""
    with db_manager.session() as session:
        jobs = session.scalars(
            select(ImportJobModel).order_by(ImportJobModel.started_at.desc()).limit(10)
        ).all()
        return [
            {
                "job_id": j.id,
                "status": j.status,
                "target_directory": j.target_directory,
                "total_files": j.total_files,
                "processed_files": j.processed_files,
                "total_rows": j.total_rows,
                "started_at": j.started_at,
                "completed_at": j.completed_at,
                "error_message": j.error_message,
            }
            for j in jobs
        ]


@router.get("/replay")
def get_replay(
    date: date,
    symbol: str | None = None,
    sector: str | None = None,
    lookback: int = Query(default=100, le=1000),
) -> list[dict[str, Any]]:
    """Point-in-time Market Replay feed guaranteed without future lookahead leakage."""
    replay_svc = MarketReplayService(db_manager.session)

    if symbol:
        candles = replay_svc.get_stock_replay(symbol, date, lookback_candles=lookback)
        return [
            {
                "symbol": c.symbol,
                "date": c.date,
                "open": c.open,
                "high": c.high,
                "low": c.low,
                "close": c.close,
                "volume": c.volume,
                "vwap": c.vwap,
            }
            for c in candles
        ]
    elif sector:
        candles = replay_svc.get_sector_replay(sector, date, lookback_candles=lookback)
        return [
            {
                "symbol": c.symbol,
                "date": c.date,
                "open": c.open,
                "high": c.high,
                "low": c.low,
                "close": c.close,
                "volume": c.volume,
            }
            for c in candles
        ]
    else:
        candles = replay_svc.get_market_snapshot(date)
        return [
            {
                "symbol": c.symbol,
                "date": c.date,
                "close": c.close,
                "volume": c.volume,
            }
            for c in candles
        ]
