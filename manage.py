#!/usr/bin/env python3
"""
Production Management CLI for MONEYYYYYY AI Hedge Fund Historical Market Data Platform.

Provides commands for dataset import, validation, market replay, database diagnostics,
indexing, backup, and health checks.
"""

import argparse
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

# Add project directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from sqlalchemy import func, select, text

from packages.infrastructure.database.config import DatabaseConfig
from packages.infrastructure.database.models import (
    CompanyModel,
    ImportJobModel,
    MarketIndexModel,
    PriceHistoryDailyModel,
    SymbolModel,
)
from packages.infrastructure.database.session import DatabaseManager
from packages.infrastructure.market_data.importer import MarketDataImporter
from packages.infrastructure.market_data.replay import MarketReplayService
from packages.infrastructure.market_data.scanner import DataScanner
from packages.infrastructure.market_data.validator import DataValidator, ValidationReport


def init_db() -> DatabaseManager:
    """Initialize database manager and ensure tables are created."""
    db_mngr = DatabaseManager()
    db_mngr.create_all()
    return db_mngr


def cmd_import_data(args: argparse.Namespace) -> None:
    """Command: Import historical market datasets."""
    db_mngr = init_db()
    cfg = db_mngr.config
    target_path = Path(args.path or cfg.market_data_path)

    print("=== MONEYYYYYY Data Importer ===")
    print(f"Scanning directory: {target_path}")

    scanner = DataScanner(target_path)
    summary = scanner.get_summary()

    print(f"Folders detected: {summary['folder_count']} {summary['folders_detected']}")
    print(
        f"Total files found: {summary['total_files']} ({summary['csv_files_count']} CSVs, {summary['zip_files_count']} ZIPs)"
    )

    discovered = scanner.scan_files()
    if not discovered:
        print("No supported market data files found to import.")
        return

    print("\nStarting ingestion pipeline...")
    importer = MarketDataImporter(db_mngr.session, batch_size=args.batch_size)
    stats = importer.import_discovered_files(
        discovered, str(target_path), resume_job_id=args.resume
    )

    print("\n=== Import Execution Finished ===")
    print(f"Job ID: {stats.job_id}")
    print(f"Status: {stats.status}")
    print(f"Files Processed: {stats.files_processed}/{stats.total_files}")
    print(f"Rows Imported: {stats.rows_imported}")
    print(f"Rows Skipped: {stats.rows_skipped}")
    if stats.error_message:
        print(f"Errors: {stats.error_message}")


def cmd_validate_data(args: argparse.Namespace) -> None:
    """Command: Perform data integrity validation on dataset files."""
    cfg = DatabaseConfig()
    target_path = Path(args.path or cfg.market_data_path)

    print("=== MONEYYYYYY Data Validator ===")
    print(f"Validating dataset under: {target_path}")

    scanner = DataScanner(target_path)
    files = scanner.scan_files()

    validator = DataValidator()
    report = ValidationReport()

    for f in files:
        validator.validate_file(f.file_path, report)

    print("\n=== Validation Summary Report ===")
    print(f"Total Files Scanned: {report.total_files_scanned}")
    print(f"Total Rows Inspected: {report.total_rows_inspected}")
    print(f"Valid Rows: {report.valid_rows_count}")
    print(f"Invalid Rows: {report.invalid_rows_count}")
    print(f"Duplicate Rows: {report.duplicate_rows_count}")
    print(f"Negative Price Issues: {report.negative_price_count}")
    print(f"Negative Volume Issues: {report.negative_volume_count}")
    print(f"OHLC Inconsistencies: {report.ohlc_inconsistency_count}")
    print(f"Invalid Date Formats: {report.invalid_date_count}")

    if report.corrupted_files:
        print(f"\nCorrupted Files ({len(report.corrupted_files)}):")
        for cf in report.corrupted_files[:10]:
            print(f" - {cf}")

    if report.issues:
        print(f"\nSample Issues Recorded ({min(5, len(report.issues))} of {len(report.issues)}):")
        for issue in report.issues[:5]:
            print(
                f" - [{issue.issue_type}] File: {issue.file_path} Row {issue.row_number}: {issue.description}"
            )

    if report.is_clean:
        print("\nDATASET IS CLEAN: Zero anomalies detected!")


def cmd_database_info(args: argparse.Namespace) -> None:
    """Command: Output database diagnostics and row counts."""
    db_mngr = init_db()
    cfg = db_mngr.config

    with db_mngr.session() as session:
        comp_cnt = session.scalar(select(func.count(CompanyModel.id))) or 0
        sym_cnt = session.scalar(select(func.count(SymbolModel.id))) or 0
        prices_cnt = session.scalar(select(func.count(PriceHistoryDailyModel.id))) or 0
        indices_cnt = session.scalar(select(func.count(MarketIndexModel.id))) or 0
        jobs_cnt = session.scalar(select(func.count(ImportJobModel.id))) or 0

        min_date = session.scalar(select(func.min(PriceHistoryDailyModel.date)))
        max_date = session.scalar(select(func.max(PriceHistoryDailyModel.date)))

    print("=== MONEYYYYYY Database Diagnostics ===")
    print(f"Connection URL: {cfg.url.split('@')[-1] if '@' in cfg.url else cfg.url}")
    print(f"Companies: {comp_cnt}")
    print(f"Symbols: {sym_cnt}")
    print(f"Daily Price Records: {prices_cnt:,}")
    print(f"Market Index Records: {indices_cnt:,}")
    print(f"Import Jobs Executed: {jobs_cnt}")
    if min_date and max_date:
        print(f"Historical Coverage Range: {min_date} -> {max_date}")


def cmd_list_symbols(args: argparse.Namespace) -> None:
    """Command: List registered market symbols."""
    db_mngr = init_db()
    with db_mngr.session() as session:
        stmt = select(SymbolModel).order_by(SymbolModel.symbol.asc())
        if args.limit:
            stmt = stmt.limit(args.limit)
        symbols = session.scalars(stmt).all()

    print(f"=== Registered Symbols ({len(symbols)}) ===")
    for s in symbols:
        print(f"{s.symbol:<12} | {s.name:<35} | {s.exchange} | {s.asset_type}")


def cmd_replay(args: argparse.Namespace) -> None:
    """Command: Execute market replay for point-in-time time travel."""
    db_mngr = init_db()
    replay_svc = MarketReplayService(db_mngr.session)

    target_date = datetime.strptime(args.date, "%Y-%m-%d").date()
    print(f"=== Market Replay Engine (Point-in-Time as of {target_date}) ===")

    if args.symbol:
        candles = replay_svc.get_stock_replay(
            args.symbol, target_date, lookback_candles=args.limit or 10
        )
        print(f"Single Stock Replay for {args.symbol.upper()} ({len(candles)} candles):")
        for c in candles:
            print(
                f"  {c.date} | O:{c.open:<8.2f} H:{c.high:<8.2f} L:{c.low:<8.2f} C:{c.close:<8.2f} Vol:{c.volume}"
            )
    elif args.sector:
        candles = replay_svc.get_sector_replay(
            args.sector, target_date, lookback_candles=args.limit or 10
        )
        print(f"Sector Replay for '{args.sector}' ({len(candles)} records):")
        for c in candles[:15]:
            print(f"  {c.symbol:<10} | {c.date} | Close:{c.close:<8.2f} Vol:{c.volume}")
    else:
        snapshot = replay_svc.get_market_snapshot(target_date)
        print(f"Market Snapshot ({len(snapshot)} tickers active as of {target_date}):")
        for c in snapshot[:20]:
            print(f"  {c.symbol:<10} | Date:{c.date} | Close:{c.close:<8.2f} Vol:{c.volume}")


def cmd_market_summary(args: argparse.Namespace) -> None:
    """Command: Output high level market summary per sector and exchange."""
    db_mngr = init_db()
    with db_mngr.session() as session:
        sectors = session.execute(
            select(CompanyModel.sector, func.count(CompanyModel.id)).group_by(CompanyModel.sector)
        ).all()

        total_rows = session.scalar(select(func.count(PriceHistoryDailyModel.id))) or 0

    print("=== MONEYYYYYY Market Summary ===")
    print(f"Total Database Rows: {total_rows:,}")
    print("\nSector Breakdown:")
    for sec, cnt in sectors:
        print(f"  - {sec or 'Uncategorized':<30}: {cnt} companies")


def cmd_import_status(args: argparse.Namespace) -> None:
    """Command: Output status of recent import jobs."""
    db_mngr = init_db()
    with db_mngr.session() as session:
        jobs = session.scalars(
            select(ImportJobModel).order_by(ImportJobModel.started_at.desc()).limit(10)
        ).all()

    print("=== Import Job Log History ===")
    for j in jobs:
        print(
            f"Job ID: {j.id} | Status: {j.status} | Processed: {j.processed_files}/{j.total_files} files | Rows: {j.total_rows:,} | Started: {j.started_at}"
        )


def cmd_rebuild_indexes(args: argparse.Namespace) -> None:
    """Command: Rebuild or optimize database table indexes."""
    db_mngr = init_db()
    print("=== Rebuilding Database Indexes ===")
    with db_mngr.session() as session:
        dialect = session.bind.dialect.name if session.bind else "sqlite"
        if dialect == "sqlite":
            session.execute(text("REINDEX;"))
            session.execute(text("VACUUM;"))
            print("SQLite REINDEX & VACUUM completed successfully.")
        elif dialect == "postgresql":
            session.execute(text("REINDEX TABLE price_history_daily;"))
            print("PostgreSQL REINDEX TABLE completed successfully.")
        session.commit()


def cmd_backup_db(args: argparse.Namespace) -> None:
    """Command: Backup local SQLite/DB file."""
    cfg = DatabaseConfig()
    print("=== Database Backup ===")
    if "sqlite" in cfg.url:
        db_file = cfg.url.replace("sqlite:///", "")
        out_file = args.out or f"backup_app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        if os.path.exists(db_file):
            shutil.copyfile(db_file, out_file)
            print(f"SQLite database backup created at: {out_file}")
        else:
            print(f"DB file '{db_file}' not found.")
    else:
        print(f"PostgreSQL backup requires pg_dump utility for connection: {cfg.url}")


def cmd_health_check(args: argparse.Namespace) -> None:
    """Command: System health check verifying database and storage connectivity."""
    db_mngr = init_db()
    cfg = db_mngr.config

    print("=== MONEYYYYYY Platform Health Check ===")
    try:
        with db_mngr.session() as session:
            session.execute(text("SELECT 1;"))
        print("[OK] Database Connection: Healthy")
    except Exception as e:
        print(f"[FAIL] Database Connection Error: {e}")

    market_data_path = Path(cfg.market_data_path)
    if market_data_path.exists():
        print(f"[OK] Market Data Storage Path '{market_data_path}': Accessible")
    else:
        print(f"[WARN] Market Data Storage Path '{market_data_path}': Directory does not exist yet")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="MONEYYYYYY AI Hedge Fund Historical Market Data CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Management command to execute")

    # import-data
    p_import = subparsers.add_parser("import-data", help="Import datasets into PostgreSQL/DB")
    p_import.add_argument("--path", type=str, help="Custom MARKET_DATA_PATH directory")
    p_import.add_argument(
        "--batch-size", type=int, default=5000, help="Batch size for bulk insertion"
    )
    p_import.add_argument("--resume", type=str, help="Resume job ID")

    # validate-data
    p_val = subparsers.add_parser(
        "validate-data", help="Validate dataset integrity & OHLC consistency"
    )
    p_val.add_argument("--path", type=str, help="Target market data path to validate")

    # database-info
    subparsers.add_parser("database-info", help="Display database statistics and record counts")

    # list-symbols
    p_sym = subparsers.add_parser("list-symbols", help="List registered stock ticker symbols")
    p_sym.add_argument("--limit", type=int, default=100, help="Max symbols to display")

    # replay
    p_rep = subparsers.add_parser("replay", help="Execute point-in-time market replay")
    p_rep.add_argument("--date", type=str, required=True, help="Target date YYYY-MM-DD")
    p_rep.add_argument("--symbol", type=str, help="Filter replay by single ticker symbol")
    p_rep.add_argument("--sector", type=str, help="Filter replay by sector")
    p_rep.add_argument("--limit", type=int, default=20, help="Limit number of candles")

    # market-summary
    subparsers.add_parser("market-summary", help="Output high level market sector summary")

    # import-status
    subparsers.add_parser("import-status", help="Show execution logs of recent import jobs")

    # rebuild-indexes
    subparsers.add_parser("rebuild-indexes", help="Rebuild and optimize database indexes")

    # backup-db
    p_bak = subparsers.add_parser("backup-db", help="Create backup copy of local database")
    p_bak.add_argument("--out", type=str, help="Output backup filepath")

    # health-check
    subparsers.add_parser("health-check", help="Run system infrastructure health checks")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    cmd_map = {
        "import-data": cmd_import_data,
        "validate-data": cmd_validate_data,
        "database-info": cmd_database_info,
        "list-symbols": cmd_list_symbols,
        "replay": cmd_replay,
        "market-summary": cmd_market_summary,
        "import-status": cmd_import_status,
        "rebuild-indexes": cmd_rebuild_indexes,
        "backup-db": cmd_backup_db,
        "health-check": cmd_health_check,
    }

    fn = cmd_map.get(args.command)
    if fn:
        fn(args)


if __name__ == "__main__":
    main()
