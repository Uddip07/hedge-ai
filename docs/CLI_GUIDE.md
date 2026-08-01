# MONEYYYYYY CLI Guide

The management CLI (`manage.py`) provides commands to manage datasets, perform health checks, run validation, and execute point-in-time market replays.

---

## Command Reference

### 1. Data Ingestion
```bash
python manage.py import-data [--path PATH] [--batch-size 5000]
```
Recursively scans `MARKET_DATA_PATH` and ingests all historical CSVs and zip archives.

### 2. Dataset Validation
```bash
python manage.py validate-data [--path PATH]
```
Scans datasets for OHLC inconsistencies (`High < Low`), negative prices, negative volumes, invalid dates, and duplicate rows.

### 3. Database Diagnostics
```bash
python manage.py database-info
```
Displays current table row counts, company counts, price records, and date coverage range.

### 4. List Registered Symbols
```bash
python manage.py list-symbols [--limit 100]
```
Lists registered equity and index symbols in the database.

### 5. Market Replay Simulation
```bash
python manage.py replay --date 2022-06-15 [--symbol RELIANCE] [--sector IT]
```
Runs a point-in-time market replay as of specified date without lookahead bias.

### 6. Market Summary
```bash
python manage.py market-summary
```
Prints breakdown of registered companies across industry sectors.

### 7. Import Job Status
```bash
python manage.py import-status
```
Displays execution status and row counts of recent import jobs.

### 8. Rebuild Indexes
```bash
python manage.py rebuild-indexes
```
Optimizes and rebuilds table indexes.

### 9. Database Backup
```bash
python manage.py backup-db [--out backup.db]
```
Creates a timestamped snapshot backup of local database.

### 10. Platform Health Check
```bash
python manage.py health-check
```
Verifies database connectivity and dataset path accessibility.
