"""
End-to-End Live Verification Script for MONEYYYYYY Native Windows Platform.
"""

import sys
from datetime import date

from sqlalchemy import func, select

from packages.api.routers.alert import DispatchAlertRequest, dispatch_alert
from packages.api.routers.backtest import BacktestRunRequest, run_backtest
from packages.api.routers.market import get_daily_market_summary, ingest_news
from packages.api.routers.market_data import SyncMarketDataRequest, sync_market_data
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.infrastructure.database.models import (
    CompanyModel,
    PriceHistoryDailyModel,
)
from packages.infrastructure.database.session import DatabaseManager
from packages.infrastructure.market_data.providers.yahoo_provider import YahooMarketDataProvider


def main() -> int:
    print("=" * 70)
    print(" MONEYYYYYY — REAL LIVE END-TO-END VERIFICATION")
    print("=" * 70)

    db_manager = DatabaseManager()
    db_manager.create_all()

    # 1. Test Yahoo Finance Provider Directly
    print("\n[1/8] Testing Live Yahoo Finance Provider...")
    yahoo = YahooMarketDataProvider()
    t = Ticker("RELIANCE.NSE")
    q = yahoo.get_quote(t)
    print(
        f"  Live Quote for RELIANCE.NSE: Price={q.price.amount} INR, Change 24h={q.change_24h}, Timestamp={q.timestamp}"
    )
    assert float(q.price.amount) > 0, "Price must be positive"

    # 2. Test Market Data Sync with Real Symbols
    print("\n[2/8] Testing Market Data Sync (RELIANCE, TCS, INFY)...")
    sync_req = SyncMarketDataRequest(symbols=["RELIANCE", "TCS", "INFY"], days=15)
    sync_res = sync_market_data(sync_req)
    print(
        f"  Sync Status: {sync_res.status}, Synced: {sync_res.symbols_synced}, Rows: {sync_res.rows_imported}"
    )
    assert sync_res.status == "COMPLETED"
    assert sync_res.symbols_synced == 3

    # 3. Verify Database Persistence
    print("\n[3/8] Verifying PostgreSQL / SQLite Database Records...")
    with db_manager.session() as session:
        for sym in ["RELIANCE", "TCS", "INFY"]:
            comp = session.scalar(select(CompanyModel).where(CompanyModel.symbol == sym))
            assert comp is not None, f"Company {sym} not found in DB"
            price_count = session.scalar(
                select(func.count(PriceHistoryDailyModel.id)).where(
                    PriceHistoryDailyModel.company_id == comp.id
                )
            )
            sample_price = session.scalar(
                select(PriceHistoryDailyModel)
                .where(PriceHistoryDailyModel.company_id == comp.id)
                .order_by(PriceHistoryDailyModel.date.desc())
                .limit(1)
            )
            print(
                f"  Company: {comp.company_name} ({comp.symbol}) | Sector: {comp.sector} | DB Rows: {price_count}"
            )
            if sample_price:
                print(
                    f"    Latest Bar: Date={sample_price.date}, Open={sample_price.open}, High={sample_price.high}, Low={sample_price.low}, Close={sample_price.close}, Vol={sample_price.volume}"
                )
            assert price_count > 0, f"Expected prices in DB for {sym}"

    # 4. Test Idempotency
    print("\n[4/8] Testing Ingestion Idempotency (Second Execution)...")
    sync_res2 = sync_market_data(sync_req)
    print(
        f"  Re-run Status: {sync_res2.status}, Synced: {sync_res2.symbols_synced}, Rows Imported: {sync_res2.rows_imported}"
    )
    assert sync_res2.rows_imported == 0, "Second sync must not insert duplicate rows"

    # 5. Test Daily Market Summary
    print("\n[5/8] Testing Daily Market Summary...")
    import asyncio

    summary = asyncio.run(get_daily_market_summary())
    print(f"  Report Date: {summary.get('report_date')}")
    print(f"  Benchmarks Available: {list(summary.get('benchmarks', {}).keys())}")
    print(f"  Top Gainers Count: {len(summary.get('top_gainers', []))}")
    print(f"  Top Losers Count: {len(summary.get('top_losers', []))}")
    assert "benchmarks" in summary

    # 6. Test News Ingestion & Deduplication
    print("\n[6/8] Testing Live News Pipeline Ingestion...")
    news_res = asyncio.run(ingest_news(["RELIANCE", "TCS"]))
    print(
        f"  News Ingest Status: {news_res.get('status')}, Articles Extracted: {len(news_res.get('articles', []))}"
    )
    if news_res.get("articles"):
        sample_news = news_res["articles"][0]
        print(
            f"  Sample Article: '{sample_news.get('title')}' | Publisher: '{sample_news.get('publisher')}' | URL: {sample_news.get('url')}"
        )
        print(
            f"  Sentiment Score: {sample_news.get('sentiment_score')}, Label: {sample_news.get('sentiment_label')}"
        )

    # 7. Test Backtest Run
    print("\n[7/8] Testing Quantitative Backtest Simulation...")
    bt_req = BacktestRunRequest(
        strategy_id="MOMENTUM_SMA",
        symbols=["RELIANCE", "TCS"],
        start_date=date(2025, 1, 1),
        end_date=date(2026, 8, 1),
        initial_capital=1000000.0,
        parameters={"sma_window": 5},
    )
    bt_res = run_backtest(bt_req)
    print(f"  Backtest Run ID: {bt_res.run_id}")
    print(
        f"  Status: {bt_res.status}, Final Value: {bt_res.final_portfolio_value:,.2f} INR, Return: {bt_res.total_return_pct:.2f}%"
    )
    print(
        f"  Sharpe Ratio: {bt_res.sharpe_ratio}, Max Drawdown: {bt_res.max_drawdown_pct}%, Total Trades: {bt_res.total_trades}"
    )
    assert bt_res.status == "COMPLETED"

    # 8. Test Alert Dispatch
    print("\n[8/8] Testing Platform Alert Dispatch & Recording...")
    alert_req = DispatchAlertRequest(
        alert_type="BACKTEST_COMPLETED",
        severity="INFO",
        source="e2e_live_test",
        title="Live E2E Verification Alert",
        message="Backtest run completed successfully during live verification.",
        metadata={"run_id": bt_res.run_id},
    )
    alert_res = dispatch_alert(alert_req)
    print(
        f"  Alert ID: {alert_res.alert_id}, Status: {alert_res.status}, Recorded: {alert_res.recorded}"
    )
    assert alert_res.status == "DISPATCHED"
    assert alert_res.recorded is True

    print("\n" + "=" * 70)
    print(" ALL LIVE END-TO-END VERIFICATION CHECKS PASSED (100% LIVE DATA)")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
