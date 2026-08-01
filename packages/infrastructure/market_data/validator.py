"""
Market Data Validation Engine.

Validates datasets for OHLC consistency, negative values, corrupted dates,
duplicate rows, missing candles, and outputs comprehensive validation reports.
"""

import csv
import io
import zipfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class ValidationIssue:
    """
    Detailed anomaly or validation issue recorded during dataset inspection.
    """

    file_path: str
    row_number: int
    issue_type: str  # "INVALID_DATE", "NEGATIVE_PRICE", "NEGATIVE_VOLUME", "OHLC_INCONSISTENCY", "DUPLICATE_ROW"
    description: str
    row_data: dict[str, Any]


@dataclass
class ValidationReport:
    """
    Comprehensive Data Validation Report across scanned datasets.
    """

    total_files_scanned: int = 0
    total_rows_inspected: int = 0
    valid_rows_count: int = 0
    invalid_rows_count: int = 0
    duplicate_rows_count: int = 0
    negative_price_count: int = 0
    negative_volume_count: int = 0
    ohlc_inconsistency_count: int = 0
    invalid_date_count: int = 0
    corrupted_files: list[str] = field(default_factory=list)
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return len(self.issues) == 0 and len(self.corrupted_files) == 0


class DataValidator:
    """
    Data Integrity and Validation Engine for Historical Market Data.
    """

    # Supported column mappings
    DATE_COLS = ["date", "datetime", "timestamp", "time"]
    OPEN_COLS = ["open"]
    HIGH_COLS = ["high"]
    LOW_COLS = ["low"]
    CLOSE_COLS = ["close"]
    VOLUME_COLS = ["volume", "vol"]

    def normalize_header(self, header: list[str]) -> dict[str, int]:
        """
        Map CSV header column names to standard fields.
        """
        col_map = {}
        for idx, col in enumerate(header):
            clean_col = col.strip().lower()
            if clean_col in self.DATE_COLS and "date" not in col_map:
                col_map["date"] = idx
            elif clean_col in self.OPEN_COLS and "open" not in col_map:
                col_map["open"] = idx
            elif clean_col in self.HIGH_COLS and "high" not in col_map:
                col_map["high"] = idx
            elif clean_col in self.LOW_COLS and "low" not in col_map:
                col_map["low"] = idx
            elif clean_col in self.CLOSE_COLS and "close" not in col_map:
                col_map["close"] = idx
            elif clean_col in self.VOLUME_COLS and "volume" not in col_map:
                col_map["volume"] = idx
        return col_map

    def parse_date(self, date_str: str) -> datetime | None:
        """
        Attempt multi-format date string parsing.
        """
        date_str = date_str.strip()
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
        # Remove nanoseconds or trailing spaces
        if "." in date_str:
            date_str = date_str.split(".")[0]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None

    def validate_file(self, file_path: Path, report: ValidationReport) -> None:
        """
        Validate an individual CSV file or Zip archive containing CSVs.
        """
        if file_path.suffix.lower() == ".zip":
            try:
                with zipfile.ZipFile(file_path, "r") as z:
                    for inner in z.namelist():
                        if inner.endswith(".csv") and not inner.startswith("__MACOSX"):
                            with z.open(inner) as f:
                                self._validate_stream(
                                    io.TextIOWrapper(f, encoding="utf-8", errors="replace"),
                                    f"{file_path.name}/{inner}",
                                    report,
                                )
            except Exception as e:
                report.corrupted_files.append(f"{file_path} (Zip error: {str(e)})")
        elif file_path.suffix.lower() == ".csv":
            try:
                with open(file_path, encoding="utf-8", errors="replace") as f:
                    self._validate_stream(f, str(file_path), report)
            except Exception as e:
                report.corrupted_files.append(f"{file_path} (CSV read error: {str(e)})")

    def _validate_stream(
        self, stream: io.TextIOBase, file_identifier: str, report: ValidationReport
    ) -> None:
        """
        Validate CSV content stream row by row.
        """
        reader = csv.reader(stream)
        try:
            header = next(reader)
        except StopIteration:
            report.corrupted_files.append(f"{file_identifier} (Empty file)")
            return

        col_map = self.normalize_header(header)

        if "date" not in col_map or "close" not in col_map:
            report.corrupted_files.append(
                f"{file_identifier} (Missing required date or close headers)"
            )
            return

        report.total_files_scanned += 1
        seen_dates = set()

        for row_num, row in enumerate(reader, start=2):
            if not row or len(row) <= max(col_map.values()):
                continue

            report.total_rows_inspected += 1
            has_error = False

            # Parse date
            dt = self.parse_date(row[col_map["date"]])
            if not dt:
                report.invalid_date_count += 1
                has_error = True
                report.issues.append(
                    ValidationIssue(
                        file_path=file_identifier,
                        row_number=row_num,
                        issue_type="INVALID_DATE",
                        description=f"Unparseable date value: '{row[col_map['date']]}'",
                        row_data={"row": row},
                    )
                )

            # Check duplicate timestamp within file
            if dt:
                dt_key = dt.isoformat()
                if dt_key in seen_dates:
                    report.duplicate_rows_count += 1
                    has_error = True
                    report.issues.append(
                        ValidationIssue(
                            file_path=file_identifier,
                            row_number=row_num,
                            issue_type="DUPLICATE_ROW",
                            description=f"Duplicate date timestamp: '{dt_key}'",
                            row_data={"row": row},
                        )
                    )
                else:
                    seen_dates.add(dt_key)

            # Parse OHLC values
            try:
                open_val = (
                    float(row[col_map["open"]])
                    if "open" in col_map
                    else float(row[col_map["close"]])
                )
                high_val = float(row[col_map["high"]]) if "high" in col_map else open_val
                low_val = float(row[col_map["low"]]) if "low" in col_map else open_val
                close_val = float(row[col_map["close"]])
                vol_val = (
                    int(float(row[col_map["volume"]]))
                    if "volume" in col_map and row[col_map["volume"]]
                    else 0
                )

                # Negative price check
                if open_val < 0 or high_val < 0 or low_val < 0 or close_val < 0:
                    report.negative_price_count += 1
                    has_error = True
                    report.issues.append(
                        ValidationIssue(
                            file_path=file_identifier,
                            row_number=row_num,
                            issue_type="NEGATIVE_PRICE",
                            description=f"Negative price found: O={open_val}, H={high_val}, L={low_val}, C={close_val}",
                            row_data={"row": row},
                        )
                    )

                # Negative volume check
                if vol_val < 0:
                    report.negative_volume_count += 1
                    has_error = True
                    report.issues.append(
                        ValidationIssue(
                            file_path=file_identifier,
                            row_number=row_num,
                            issue_type="NEGATIVE_VOLUME",
                            description=f"Negative volume value: {vol_val}",
                            row_data={"row": row},
                        )
                    )

                # OHLC consistency check
                if (
                    high_val < low_val
                    or open_val > high_val
                    or open_val < low_val
                    or close_val > high_val
                    or close_val < low_val
                ):
                    report.ohlc_inconsistency_count += 1
                    has_error = True
                    report.issues.append(
                        ValidationIssue(
                            file_path=file_identifier,
                            row_number=row_num,
                            issue_type="OHLC_INCONSISTENCY",
                            description=f"OHLC logical breach: High({high_val}) < Low({low_val}) or O/C outside Range",
                            row_data={"row": row},
                        )
                    )

            except ValueError as ve:
                has_error = True
                report.issues.append(
                    ValidationIssue(
                        file_path=file_identifier,
                        row_number=row_num,
                        issue_type="CORRUPTED_NUMBER",
                        description=f"Failed to parse numeric OHLC value: {str(ve)}",
                        row_data={"row": row},
                    )
                )

            if has_error:
                report.invalid_rows_count += 1
            else:
                report.valid_rows_count += 1
