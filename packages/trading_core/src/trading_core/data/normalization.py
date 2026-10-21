"""Normalization helpers for ingestion."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from trading_core.core.types import EconomicEvent, MarketBar
from trading_core.data.exceptions import DataValidationError


def parse_datetime(value: Any, field_name: str) -> datetime:
    """Parse datetime and normalize to UTC."""
    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, str):
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    else:
        raise DataValidationError(f"invalid datetime for {field_name}: {value!r}")

    if dt.tzinfo is None or dt.utcoffset() is None:
        raise DataValidationError(f"datetime for {field_name} must be timezone-aware")
    return dt.astimezone(UTC)


def parse_decimal(value: Any, field_name: str) -> Decimal | None:
    """Parse optional decimal values."""
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError) as exc:
        raise DataValidationError(f"invalid decimal for {field_name}: {value!r}") from exc


def parse_required_decimal(value: Any, field_name: str) -> Decimal:
    """Parse required decimal fields."""
    parsed = parse_decimal(value, field_name)
    if parsed is None:
        raise DataValidationError(f"missing decimal for {field_name}")
    return parsed


def normalize_market_bar(record: Mapping[str, Any], source: str) -> MarketBar:
    """Normalize a raw mapping into a validated MarketBar."""
    try:
        instrument = str(record["instrument"]).upper()
        timestamp = parse_datetime(record["timestamp"], "timestamp")
        available_raw = record.get("available_at", record["timestamp"])
        available_at = parse_datetime(available_raw, "available_at")

        return MarketBar(
            instrument=instrument,
            timestamp=timestamp,
            open=parse_required_decimal(record["open"], "open"),
            high=parse_required_decimal(record["high"], "high"),
            low=parse_required_decimal(record["low"], "low"),
            close=parse_required_decimal(record["close"], "close"),
            volume=parse_decimal(record.get("volume"), "volume"),
            bid=parse_decimal(record.get("bid"), "bid"),
            ask=parse_decimal(record.get("ask"), "ask"),
            source=str(record.get("source", source)),
            available_at=available_at,
        )
    except KeyError as exc:
        raise DataValidationError(f"missing field: {exc.args[0]}") from exc


def normalize_economic_event(record: Mapping[str, Any], source: str) -> EconomicEvent:
    """Normalize a raw mapping into a validated EconomicEvent."""
    try:
        available_raw = record.get("available_at", record["publication_time"])
        return EconomicEvent(
            event_id=str(record["event_id"]),
            name=str(record["name"]),
            instrument=str(record["instrument"]).upper() if record.get("instrument") else None,
            event_time=parse_datetime(record["event_time"], "event_time"),
            publication_time=parse_datetime(record["publication_time"], "publication_time"),
            revision_time=(
                parse_datetime(record["revision_time"], "revision_time")
                if record.get("revision_time") is not None
                else None
            ),
            actual=float(record["actual"]) if record.get("actual") is not None else None,
            forecast=float(record["forecast"]) if record.get("forecast") is not None else None,
            previous=float(record["previous"]) if record.get("previous") is not None else None,
            source=str(record.get("source", source)),
            available_at=parse_datetime(available_raw, "available_at"),
        )
    except KeyError as exc:
        raise DataValidationError(f"missing field: {exc.args[0]}") from exc
