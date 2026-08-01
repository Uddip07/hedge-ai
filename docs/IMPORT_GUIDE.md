# MONEYYYYYY Historical Data Import Guide

This guide details the auto-discovery, validation, and ingestion pipeline for importing historical stock market datasets into PostgreSQL.

---

## Directory Auto-Discovery

The importer recursively scans `MARKET_DATA_PATH` (e.g. `D:\MarketData`).
Zero folder names are hardcoded. Whether dataset folders are named:

- `data1`
- `data2`
- `data3`
- `data4`
- `data5` (added in future)
- `archive` (added in future)

the engine automatically detects every folder and nested directory.

---

## Column Variation Mapping

The CSV importer automatically maps non-standard column headers:

| Standard Key | Supported Column Variations |
|---|---|
| Date | `date`, `DATE`, `datetime`, `timestamp`, `time` |
| Open | `open`, `OPEN`, `open_price` |
| High | `high`, `HIGH`, `high_price` |
| Low | `low`, `LOW`, `low_price` |
| Close | `close`, `CLOSE`, `close_price` |
| Adjusted Close | `Adj Close`, `Adjusted Close`, `adj_close` |
| Volume | `volume`, `VOLUME`, `traded_qty` |
| VWAP | `vwap`, `VWAP`, `avg_price` |
| Delivery Quantity | `delivery`, `Delivery Quantity`, `delivery_qty` |

---

## Incremental & Resumable Ingestion

The import pipeline logs every run in `import_jobs` and `import_logs`.
If an import job is interrupted, running:

```bash
python manage.py import-data --resume <JOB_ID>
```

will automatically skip previously completed files and resume remaining ingestion without duplicating rows.
