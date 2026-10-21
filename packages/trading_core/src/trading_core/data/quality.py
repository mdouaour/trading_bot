"""Deterministic data quality checks."""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from trading_core.core.types import MarketBar
from trading_core.data.exceptions import DataQualityError


def validate_market_bar_quality(
    bar: MarketBar,
    *,
    max_spread: Decimal = Decimal("10"),
    max_delay: timedelta = timedelta(days=2),
) -> None:
    """Apply quality constraints for market bars."""
    if bar.bid is not None and bar.ask is not None and (bar.ask - bar.bid) > max_spread:
        msg = f"spread too wide: {bar.ask - bar.bid} > {max_spread}"
        raise DataQualityError(msg)

    if bar.available_at - bar.timestamp > max_delay:
        msg = f"data delay too large: {bar.available_at - bar.timestamp}"
        raise DataQualityError(msg)
