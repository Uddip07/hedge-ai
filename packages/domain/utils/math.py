"""
Financial Math Helpers for the Indian AI Hedge Fund Domain.

Provides high-precision Decimal arithmetic, rounding modes, percentage returns,
drawdowns, Sharpe ratios, and CAGR calculations. Zero float precision errors.
"""

from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Any

from packages.domain.exceptions import ValidationError


def to_decimal(val: Any) -> Decimal:
    """
    Safely convert any numeric type (int, str, Decimal, float) to Decimal.
    Converts float via string representation to avoid IEEE-754 precision artifacts.
    """
    if isinstance(val, Decimal):
        return val
    if isinstance(val, float):
        return Decimal(str(val))
    try:
        return Decimal(str(val))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValidationError(
            f"Cannot convert value '{val}' to Decimal.",
            context={"val": str(val)},
        ) from exc


def round_currency(amount: Decimal, decimals: int = 2) -> Decimal:
    """
    Round a monetary Decimal to fixed currency decimal places using standard ROUND_HALF_UP.
    """
    dec_amount = to_decimal(amount)
    quantizer = Decimal("10") ** (-decimals)
    return dec_amount.quantize(quantizer, rounding=ROUND_HALF_UP)


def calculate_return(initial_value: Decimal, final_value: Decimal) -> Decimal:
    """
    Calculate percentage return: ((final - initial) / initial) * 100.

    Raises:
        ValidationError: If initial_value is zero.
    """
    init_dec = to_decimal(initial_value)
    final_dec = to_decimal(final_value)

    if init_dec == Decimal("0"):
        raise ValidationError("Initial value cannot be zero when calculating returns.")

    pct_return = ((final_dec - init_dec) / init_dec) * Decimal("100")
    return round_currency(pct_return, decimals=4)


def calculate_drawdown(current_value: Decimal, peak_value: Decimal) -> Decimal:
    """
    Calculate peak-to-trough drawdown percentage: ((peak - current) / peak) * 100.

    Returns:
        Decimal: Non-negative drawdown percentage [0, 100].
    """
    curr_dec = to_decimal(current_value)
    peak_dec = to_decimal(peak_value)

    if peak_dec <= Decimal("0"):
        return Decimal("0.0000")

    if curr_dec >= peak_dec:
        return Decimal("0.0000")

    dd = ((peak_dec - curr_dec) / peak_dec) * Decimal("100")
    return round_currency(dd, decimals=4)


def calculate_sharpe_ratio(
    mean_return: Decimal,
    risk_free_rate: Decimal,
    std_dev: Decimal,
) -> Decimal:
    """
    Calculate Sharpe Ratio: (mean_return - risk_free_rate) / std_dev.

    Raises:
        ValidationError: If std_dev <= 0.
    """
    mean_dec = to_decimal(mean_return)
    rf_dec = to_decimal(risk_free_rate)
    sd_dec = to_decimal(std_dev)

    if sd_dec <= Decimal("0"):
        raise ValidationError(
            "Standard deviation must be strictly positive (> 0) for Sharpe Ratio."
        )

    sharpe = (mean_dec - rf_dec) / sd_dec
    return round_currency(sharpe, decimals=4)


def calculate_cagr(
    start_value: Decimal,
    end_value: Decimal,
    years: Decimal,
) -> Decimal:
    """
    Calculate Compound Annual Growth Rate (CAGR) percentage:
    ((end_value / start_value) ** (1 / years) - 1) * 100

    Raises:
        ValidationError: If start_value <= 0 or years <= 0.
    """
    start_dec = to_decimal(start_value)
    end_dec = to_decimal(end_value)
    years_dec = to_decimal(years)

    if start_dec <= Decimal("0"):
        raise ValidationError("Start value must be strictly positive for CAGR calculation.")
    if years_dec <= Decimal("0"):
        raise ValidationError("Years parameter must be strictly positive for CAGR calculation.")

    # Calculate using float exponentiation then convert back to Decimal safely
    ratio = float(end_dec / start_dec)
    exponent = 1.0 / float(years_dec)
    cagr_float = (ratio**exponent - 1.0) * 100.0

    return round_currency(to_decimal(cagr_float), decimals=4)
