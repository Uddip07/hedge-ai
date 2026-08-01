"""
Unit and Integration Tests for Historical Market Data Platform.
"""

from datetime import date

import pytest
from sqlalchemy import select

from packages.infrastructure.database.config import DatabaseConfig
from packages.infrastructure.database.models import (
    CompanyModel,
)
from packages.infrastructure.database.session import DatabaseManager
from packages.infrastructure.market_data.feature_engine import FeatureEngine, FeatureRecord
from packages.infrastructure.market_data.importer import MarketDataImporter
from packages.infrastructure.market_data.replay import MarketReplayService
from packages.infrastructure.market_data.scanner import DataScanner
from packages.infrastructure.market_data.validator import DataValidator, ValidationReport


@pytest.fixture
def temp_db():
    """Create an in-memory SQLite database for test execution."""
    config = DatabaseConfig(url="sqlite:///:memory:")
    db = DatabaseManager(config)
    db.create_all()
    yield db
    db.drop_all()


def test_scanner_auto_discovery(tmp_path):
    """Test dynamic folder and CSV/Zip scanner without hardcoded folder names."""
    d1 = tmp_path / "data1"
    d1.mkdir()
    f1 = d1 / "RELIANCE_minute.csv"
    f1.write_text("date,open,high,low,close,volume\n2022-01-01,100,105,95,102,1000\n")

    d2 = tmp_path / "data_custom_99"
    d2.mkdir()
    f2 = d2 / "TRENT_daily.csv"
    f2.write_text("date,open,high,low,close,volume\n2022-01-01,500,510,490,505,500\n")

    scanner = DataScanner(tmp_path)
    summary = scanner.get_summary()

    assert summary["folder_count"] == 2
    assert "data1" in summary["folders_detected"]
    assert "data_custom_99" in summary["folders_detected"]
    assert summary["total_files"] == 2


def test_validator_detects_anomalies(tmp_path):
    """Test validation engine detects negative prices and OHLC breaches."""
    bad_csv = tmp_path / "bad.csv"
    bad_csv.write_text(
        "date,open,high,low,close,volume\n"
        "2022-01-01,100,90,110,105,1000\n"  # High < Low inconsistency
        "2022-01-02,-50,100,40,90,1000\n"  # Negative open price
    )

    validator = DataValidator()
    report = ValidationReport()
    validator.validate_file(bad_csv, report)

    assert report.total_rows_inspected == 2
    assert report.ohlc_inconsistency_count >= 1
    assert report.negative_price_count >= 1
    assert not report.is_clean


def test_importer_and_replay_engine(temp_db, tmp_path):
    """Test dataset ingestion and zero-lookahead point-in-time market replay."""
    data_dir = tmp_path / "data1"
    data_dir.mkdir()
    csv_file = data_dir / "INFY_minute.csv"
    csv_file.write_text(
        "date,open,high,low,close,volume\n"
        "2022-01-01,1500,1520,1490,1510,5000\n"
        "2022-01-02,1510,1530,1500,1525,6000\n"
        "2022-01-05,1525,1550,1520,1540,7000\n"
    )

    scanner = DataScanner(tmp_path)
    files = scanner.scan_files()

    importer = MarketDataImporter(temp_db.session, batch_size=10)
    stats = importer.import_discovered_files(files, str(tmp_path))

    assert stats.files_processed == 1
    assert stats.rows_imported == 3

    # Verify company created
    with temp_db.session() as session:
        comp = session.scalar(select(CompanyModel).where(CompanyModel.symbol == "INFY"))
        assert comp is not None
        assert comp.symbol == "INFY"

    # Test Market Replay strictly on or before 2022-01-02 (must NOT return 2022-01-05 candle)
    replay_svc = MarketReplayService(temp_db.session)
    candles = replay_svc.get_stock_replay("INFY", target_date=date(2022, 1, 2))

    assert len(candles) == 2
    assert max(c.date for c in candles) == date(2022, 1, 2)


def test_feature_engine(temp_db):
    """Test quantitative feature calculation and feature store persistence."""
    fe = FeatureEngine(temp_db.session)

    # Calculate returns
    prices = [100.0, 105.0, 102.0, 108.0]
    returns = fe.compute_basic_returns(prices)
    assert len(returns) == 3
    assert pytest.approx(returns[0]) == 0.05

    # Test feature save
    with temp_db.session() as session:
        comp = CompanyModel(id="comp-123", symbol="TCS", company_name="TCS Ltd", exchange="NSE")
        session.add(comp)
        session.commit()

    record = FeatureRecord(
        company_id="comp-123",
        date=date(2022, 1, 1),
        feature_name="RSI_14",
        feature_value=65.5,
        feature_version="v1.0",
    )
    fe.save_features([record])

    features = fe.get_features("comp-123", date(2022, 1, 1))
    assert "RSI_14" in features
    assert features["RSI_14"] == 65.5
