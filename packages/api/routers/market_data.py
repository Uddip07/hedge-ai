"""
FastAPI Router for Historical Market Data Platform.

Exposes REST API endpoints for data import, job tracking, database statistics,
symbol/company lookups, historical prices, market replay, and backtesting feeds.
"""

import uuid
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, select

from packages.api.dependencies import verify_automation_key
from packages.domain.enums.market import Timeframe
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.domain.value_objects.temporal.timestamps import Timestamp
from packages.infrastructure.database.config import DatabaseConfig
from packages.infrastructure.database.models import (
    CompanyModel,
    ImportJobModel,
    PriceHistoryDailyModel,
    SymbolModel,
)
from packages.infrastructure.database.session import DatabaseManager
from packages.infrastructure.market_data.importer import MarketDataImporter
from packages.infrastructure.market_data.providers.yahoo_provider import YahooMarketDataProvider
from packages.infrastructure.market_data.replay import MarketReplayService
from packages.infrastructure.market_data.scanner import DataScanner

router = APIRouter(prefix="/api/v1/market-data", tags=["Market Data Platform"])
db_manager = DatabaseManager()


def _to_float(val: Any) -> float:
    if hasattr(val, "amount"):
        return float(val.amount)
    if hasattr(val, "value"):
        return float(val.value)
    return float(val)


def _to_int(val: Any) -> int:
    if hasattr(val, "value"):
        return int(val.value)
    if hasattr(val, "quantity"):
        return int(val.quantity)
    return int(val)


class SyncMarketDataRequest(BaseModel):
    symbols: list[str] = Field(
        default_factory=lambda: ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN"]
    )
    days: int = Field(default=30, ge=1, le=365)


class SyncMarketDataResponse(BaseModel):
    job_id: str
    status: str
    symbols_requested: int
    symbols_synced: int
    rows_imported: int
    synced_symbols: list[str]
    errors: list[dict[str, str]]
    started_at: str
    completed_at: str


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


@router.post(
    "/sync", response_model=SyncMarketDataResponse, dependencies=[Depends(verify_automation_key)]
)
def sync_market_data(payload: SyncMarketDataRequest | None = None) -> SyncMarketDataResponse:
    """
    Orchestrate market data ingestion directly from Yahoo Finance provider into database.
    Validates quotes and OHLCV daily history, upserts Company and Symbol records,
    and idempotently persists price history without duplicates.
    """
    req = payload or SyncMarketDataRequest()
    job_id = str(uuid.uuid4())
    started_at = datetime.now(UTC)

    provider = YahooMarketDataProvider()
    total_imported = 0
    synced_symbols: list[str] = []
    errors: list[dict[str, str]] = []

    # Record job in database
    with db_manager.session() as session:
        job = ImportJobModel(
            id=job_id,
            status="RUNNING",
            target_directory="YAHOO_FINANCE_SYNC",
            total_files=len(req.symbols),
            processed_files=0,
            total_rows=0,
            started_at=started_at,
        )
        session.add(job)

    start_time_iso = (
        (datetime.now(UTC) - timedelta(days=req.days))
        .replace(hour=0, minute=0, second=0)
        .isoformat()
    )
    end_time_iso = datetime.now(UTC).isoformat()
    start_ts = Timestamp.from_iso(start_time_iso)
    end_ts = Timestamp.from_iso(end_time_iso)

    for raw_symbol in req.symbols:
        clean_sym = raw_symbol.strip().upper()
        if not clean_sym:
            continue
        ticker_str = (
            f"{clean_sym}.NSE"
            if "." not in clean_sym and not clean_sym.startswith("^")
            else clean_sym
        )

        try:
            t = Ticker(ticker_str)
            profile = provider.get_company_profile(t)
            candles = provider.get_historical_ohlcv(t, Timeframe.DAY_1, start_ts, end_ts)

            with db_manager.session() as session:
                # Upsert Company
                existing_company = session.scalar(
                    select(CompanyModel).where(CompanyModel.symbol == clean_sym)
                )
                if not existing_company:
                    company_id = str(uuid.uuid4())
                    company = CompanyModel(
                        id=company_id,
                        symbol=clean_sym,
                        company_name=profile.name if profile and profile.name else clean_sym,
                        exchange="NSE",
                        sector=profile.sector.value if profile and profile.sector else "LARGE_CAP",
                        industry=profile.industry if profile and profile.industry else "General",
                        listing_status="ACTIVE",
                    )
                    session.add(company)
                    session.flush()
                else:
                    company_id = existing_company.id

                # Upsert Symbol
                existing_symbol = session.scalar(
                    select(SymbolModel).where(SymbolModel.symbol == clean_sym)
                )
                if not existing_symbol:
                    sym_entry = SymbolModel(
                        id=str(uuid.uuid4()),
                        symbol=clean_sym,
                        name=profile.name if profile and profile.name else clean_sym,
                        exchange="NSE",
                        asset_type="EQUITY",
                        is_active=True,
                    )
                    session.add(sym_entry)

                # Persist price history candles idempotently
                for candle in candles:
                    if isinstance(candle.timestamp, Timestamp):
                        candle_date = candle.timestamp.value.date()
                    elif isinstance(candle.timestamp, datetime):
                        candle_date = candle.timestamp.date()
                    elif isinstance(candle.timestamp, date):
                        candle_date = candle.timestamp
                    elif hasattr(candle.timestamp, "value") and hasattr(
                        candle.timestamp.value, "date"
                    ):
                        candle_date = candle.timestamp.value.date()
                    else:
                        candle_date = date.fromisoformat(str(candle.timestamp)[:10])
                    existing_price = session.scalar(
                        select(PriceHistoryDailyModel).where(
                            PriceHistoryDailyModel.company_id == company_id,
                            PriceHistoryDailyModel.date == candle_date,
                        )
                    )
                    if not existing_price:
                        open_val = _to_float(candle.open)
                        high_val = _to_float(candle.high)
                        low_val = _to_float(candle.low)
                        close_val = _to_float(candle.close)
                        vol_val = _to_int(candle.volume)

                        price_record = PriceHistoryDailyModel(
                            id=str(uuid.uuid4()),
                            company_id=company_id,
                            date=candle_date,
                            open=open_val,
                            high=high_val,
                            low=low_val,
                            close=close_val,
                            adjusted_close=close_val,
                            volume=vol_val,
                            vwap=close_val,
                        )
                        session.add(price_record)
                        total_imported += 1

                synced_symbols.append(clean_sym)

        except Exception as exc:
            errors.append({"symbol": clean_sym, "error": str(exc)})

    completed_at = datetime.now(UTC)
    final_status = "COMPLETED" if not errors else ("PARTIAL" if synced_symbols else "FAILED")

    # Update job record
    with db_manager.session() as session:
        job_record: ImportJobModel | None = session.get(ImportJobModel, job_id)
        if job_record is not None:
            job_record.status = final_status
            job_record.processed_files = len(synced_symbols)
            job_record.total_rows = total_imported
            job_record.completed_at = completed_at
            if errors:
                job_record.error_message = "; ".join(f"{e['symbol']}: {e['error']}" for e in errors)

    return SyncMarketDataResponse(
        job_id=job_id,
        status=final_status,
        symbols_requested=len(req.symbols),
        symbols_synced=len(synced_symbols),
        rows_imported=total_imported,
        synced_symbols=synced_symbols,
        errors=errors,
        started_at=started_at.isoformat(),
        completed_at=completed_at.isoformat(),
    )
