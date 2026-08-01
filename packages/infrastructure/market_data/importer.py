"""
High-Performance Market Data Import Engine.

Executes incremental bulk CSV ingestion into PostgreSQL/SQLite database tables
(companies, symbols, price_history_daily, import_jobs, import_logs) with column header mapping,
resumable job tracking, and duplicate row handling.
"""

import csv
import io
import logging
import uuid
import zipfile
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import insert, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session

from packages.infrastructure.database.models import (
    CompanyModel,
    ImportJobModel,
    ImportLogModel,
    PriceHistoryDailyModel,
    SymbolModel,
)

logger = logging.getLogger(__name__)


@dataclass
class ImportStats:
    """Statistics for an import execution."""

    job_id: str
    files_processed: int = 0
    total_files: int = 0
    rows_imported: int = 0
    rows_skipped: int = 0
    companies_created: int = 0
    symbols_created: int = 0
    status: str = "COMPLETED"
    error_message: str | None = None


class MarketDataImporter:
    """
    High-Throughput Bulk Import Engine.
    """

    COLUMN_VARIANTS = {
        "date": ["date", "datetime", "timestamp", "time", "date/time"],
        "open": ["open", "open_price", "op"],
        "high": ["high", "high_price", "hi"],
        "low": ["low", "low_price", "lo"],
        "close": ["close", "close_price", "cl"],
        "adjusted_close": ["adj close", "adjusted close", "adj_close", "adjusted_close"],
        "volume": ["volume", "vol", "traded_qty", "total_traded_quantity"],
        "vwap": ["vwap", "avg_price", "average_price"],
        "delivery_quantity": ["delivery", "delivery quantity", "delivery_qty", "deliv_qty"],
        "turnover": ["turnover", "total_turnover", "value", "val"],
    }

    def __init__(self, session_factory: Any, batch_size: int = 5000) -> None:
        self.session_factory = session_factory
        self.batch_size = batch_size

    def map_columns(self, header: list[str]) -> dict[str, int]:
        """
        Map CSV header names to model attribute keys based on column variants.
        """
        col_map = {}
        header_clean = [h.strip().lower() for h in header]

        for target_key, variants in self.COLUMN_VARIANTS.items():
            for idx, h in enumerate(header_clean):
                if h in variants and target_key not in col_map:
                    col_map[target_key] = idx
                    break
        return col_map

    def parse_datetime(self, val_str: str) -> datetime | None:
        """Parse datetime or date strings into datetime object."""
        val_str = val_str.strip()
        if "." in val_str:
            val_str = val_str.split(".")[0]

        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S%z",
            "%Y-%m-%d",
            "%d-%m-%Y %H:%M:%S",
            "%d-%m-%Y",
            "%Y/%m/%d %H:%M:%S",
            "%Y/%m/%d",
            "%d/%m/%Y",
        ]
        for fmt in formats:
            try:
                return datetime.strptime(val_str, fmt)
            except ValueError:
                continue
        return None

    def get_or_create_company(
        self, session: Session, symbol: str, name: str | None = None
    ) -> CompanyModel:
        """Fetch or create CompanyModel record."""
        clean_sym = symbol.strip().upper()
        stmt = select(CompanyModel).where(CompanyModel.symbol == clean_sym)
        company = session.execute(stmt).scalar_one_or_none()

        if not company:
            company = CompanyModel(
                id=str(uuid.uuid4()),
                symbol=clean_sym,
                company_name=name or f"{clean_sym} Limited",
                exchange="NSE",
                listing_status="ACTIVE",
            )
            session.add(company)

            # Ensure SymbolModel also exists
            stmt_sym = select(SymbolModel).where(SymbolModel.symbol == clean_sym)
            sym = session.execute(stmt_sym).scalar_one_or_none()
            if not sym:
                session.add(
                    SymbolModel(
                        id=str(uuid.uuid4()),
                        symbol=clean_sym,
                        name=company.company_name,
                        exchange="NSE",
                        asset_type="EQUITY",
                    )
                )
            session.flush()
        return company

    def create_import_job(
        self, session: Session, target_directory: str, total_files: int
    ) -> ImportJobModel:
        """Initialize import job record in database."""
        job = ImportJobModel(
            id=str(uuid.uuid4()),
            status="IN_PROGRESS",
            target_directory=str(target_directory),
            total_files=total_files,
            started_at=datetime.now(UTC),
        )
        session.add(job)
        session.commit()
        return job

    def import_discovered_files(
        self, files: list[Any], target_directory: str, resume_job_id: str | None = None
    ) -> ImportStats:
        """
        Ingest a list of DiscoveredFile objects with batching and state tracking.
        """
        with self.session_factory() as session:
            if resume_job_id:
                job = session.get(ImportJobModel, resume_job_id)
                if not job:
                    job = self.create_import_job(session, target_directory, len(files))
            else:
                job = self.create_import_job(session, target_directory, len(files))

            job_id = job.id

        stats = ImportStats(job_id=job_id, total_files=len(files))

        # Check existing completed logs for resume functionality
        processed_paths = set()
        with self.session_factory() as session:
            existing_logs = session.scalars(
                select(ImportLogModel.file_path).where(
                    ImportLogModel.job_id == job_id, ImportLogModel.status == "SUCCESS"
                )
            ).all()
            processed_paths = set(existing_logs)

        for disc_file in files:
            file_str = str(disc_file.relative_path)
            if file_str in processed_paths:
                stats.files_processed += 1
                continue

            # Process single file
            rows_imp, rows_skip, err_msg = self.import_single_file(disc_file, job_id)
            stats.files_processed += 1
            stats.rows_imported += rows_imp
            stats.rows_skipped += rows_skip

            # Update job progress periodically
            with self.session_factory() as session:
                j = session.get(ImportJobModel, job_id)
                if j:
                    j.processed_files = stats.files_processed
                    j.total_rows = stats.rows_imported
                    session.commit()

        # Mark job finished
        with self.session_factory() as session:
            j = session.get(ImportJobModel, job_id)
            if j:
                j.status = "COMPLETED" if not stats.error_message else "FAILED"
                j.completed_at = datetime.now(UTC)
                j.total_rows = stats.rows_imported
                j.error_message = stats.error_message
                session.commit()

        return stats

    def import_single_file(self, disc_file: Any, job_id: str) -> tuple[int, int, str | None]:
        """
        Parse and insert market records from a CSV file or Zip container.
        """
        rows_imported = 0
        rows_skipped = 0
        error_msg = None

        with self.session_factory() as session:
            company = self.get_or_create_company(session, disc_file.estimated_symbol)
            company_id = company.id
            session.commit()

        file_path = disc_file.file_path

        try:
            if disc_file.file_type == "csv":
                with open(file_path, encoding="utf-8", errors="replace") as f:
                    rows_imported, rows_skipped = self._process_csv_stream(f, company_id)
            elif disc_file.file_type == "zip":
                with zipfile.ZipFile(file_path, "r") as z:
                    for inner in z.namelist():
                        if inner.endswith(".csv") and not inner.startswith("__MACOSX"):
                            with z.open(inner) as f:
                                imp, skip = self._process_csv_stream(
                                    io.TextIOWrapper(f, encoding="utf-8", errors="replace"),
                                    company_id,
                                )
                                rows_imported += imp
                                rows_skipped += skip

            status_str = "SUCCESS"
        except Exception as e:
            status_str = "FAILED"
            error_msg = str(e)
            logger.error(f"Failed importing {file_path}: {e}")

        # Log completion
        with self.session_factory() as session:
            log_entry = ImportLogModel(
                id=str(uuid.uuid4()),
                job_id=job_id,
                file_path=str(disc_file.relative_path),
                status=status_str,
                rows_imported=rows_imported,
                rows_skipped=rows_skipped,
                error_details=error_msg,
            )
            session.add(log_entry)
            session.commit()

        return rows_imported, rows_skipped, error_msg

    def _process_csv_stream(self, stream: io.TextIOBase, company_id: str) -> tuple[int, int]:
        """
        Parse rows from stream and perform bulk upsert / insert into price_history_daily.
        """
        reader = csv.reader(stream)
        try:
            header = next(reader)
        except StopIteration:
            return 0, 0

        col_map = self.map_columns(header)
        if "date" not in col_map or "close" not in col_map:
            return 0, 0

        batch: list[dict[str, Any]] = []
        rows_imported = 0
        rows_skipped = 0

        for row in reader:
            if not row or len(row) <= max(col_map.values()):
                rows_skipped += 1
                continue

            dt = self.parse_datetime(row[col_map["date"]])
            if not dt:
                rows_skipped += 1
                continue

            try:
                open_p = (
                    float(row[col_map["open"]])
                    if "open" in col_map
                    else float(row[col_map["close"]])
                )
                close_p = float(row[col_map["close"]])
                high_p = float(row[col_map["high"]]) if "high" in col_map else max(open_p, close_p)
                low_p = float(row[col_map["low"]]) if "low" in col_map else min(open_p, close_p)
                adj_close = (
                    float(row[col_map["adjusted_close"]])
                    if "adjusted_close" in col_map and row[col_map["adjusted_close"]]
                    else close_p
                )
                vol = (
                    int(float(row[col_map["volume"]]))
                    if "volume" in col_map and row[col_map["volume"]]
                    else 0
                )
                vwap_val = (
                    float(row[col_map["vwap"]])
                    if "vwap" in col_map and row[col_map["vwap"]]
                    else None
                )
                deliv_qty = (
                    int(float(row[col_map["delivery_quantity"]]))
                    if "delivery_quantity" in col_map and row[col_map["delivery_quantity"]]
                    else None
                )
                turnover_val = (
                    float(row[col_map["turnover"]])
                    if "turnover" in col_map and row[col_map["turnover"]]
                    else None
                )

                record = {
                    "id": str(uuid.uuid4()),
                    "company_id": company_id,
                    "date": dt.date(),
                    "open": open_p,
                    "high": high_p,
                    "low": low_p,
                    "close": close_p,
                    "adjusted_close": adj_close,
                    "volume": vol,
                    "vwap": vwap_val,
                    "delivery_quantity": deliv_qty,
                    "turnover": turnover_val,
                }
                batch.append(record)

                if len(batch) >= self.batch_size:
                    imp, skip = self._flush_batch(batch)
                    rows_imported += imp
                    rows_skipped += skip
                    batch.clear()

            except Exception:
                rows_skipped += 1

        if batch:
            imp, skip = self._flush_batch(batch)
            rows_imported += imp
            rows_skipped += skip
            batch.clear()

        return rows_imported, rows_skipped

    def _flush_batch(self, records: list[dict[str, Any]]) -> tuple[int, int]:
        """
        Execute batch insert using dialect-appropriate bulk insert handling.
        """
        if not records:
            return 0, 0

        with self.session_factory() as session:
            try:
                # Use insert().values() with session execution
                stmt = insert(PriceHistoryDailyModel).values(records)

                # Attempt execution
                dialect = session.bind.dialect.name if session.bind else "sqlite"
                if dialect == "postgresql":
                    stmt = pg_insert(PriceHistoryDailyModel).values(records)
                    stmt = stmt.on_conflict_do_nothing(index_elements=["company_id", "date"])
                elif dialect == "sqlite":
                    stmt = sqlite_insert(PriceHistoryDailyModel).values(records)
                    stmt = stmt.on_conflict_do_nothing(index_elements=["company_id", "date"])

                session.execute(stmt)
                session.commit()
                return len(records), 0
            except Exception as e:
                session.rollback()
                # Fallback to row-by-row insert skipping duplicates
                imported = 0
                skipped = 0
                for r in records:
                    try:
                        session.execute(insert(PriceHistoryDailyModel).values(r))
                        session.commit()
                        imported += 1
                    except Exception:
                        session.rollback()
                        skipped += 1
                return imported, skipped
