from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest
from trading_core.data.exceptions import DataQualityError, DataValidationError
from trading_core.data.ingestion import DataIngestionPipeline


def test_ingest_market_bars_deduplicates_records() -> None:
    pipeline = DataIngestionPipeline()
    rows = [
        {
            "instrument": "xauusd",
            "timestamp": "2026-10-21T12:00:00Z",
            "open": "2600",
            "high": "2605",
            "low": "2598",
            "close": "2602",
            "available_at": "2026-10-21T12:00:01Z",
        },
        {
            "instrument": "XAUUSD",
            "timestamp": "2026-10-21T12:00:00Z",
            "open": "2600",
            "high": "2605",
            "low": "2598",
            "close": "2602",
            "available_at": "2026-10-21T12:00:01Z",
        },
    ]

    bars, stats = pipeline.ingest_market_bars(rows, source="feed_a")

    assert len(bars) == 1
    assert bars[0].instrument == "XAUUSD"
    assert stats.input_records == 2
    assert stats.output_records == 1
    assert stats.duplicate_records == 1


def test_ingest_market_bars_rejects_bad_quality_spread() -> None:
    pipeline = DataIngestionPipeline(max_spread=Decimal("1"))

    with pytest.raises(DataQualityError):
        pipeline.ingest_market_bars(
            [
                {
                    "instrument": "XAUUSD",
                    "timestamp": "2026-10-21T12:00:00Z",
                    "open": "2600",
                    "high": "2605",
                    "low": "2598",
                    "close": "2602",
                    "bid": "2600",
                    "ask": "2605",
                    "available_at": "2026-10-21T12:00:02Z",
                },
            ],
            source="feed_a",
        )


def test_ingest_market_bars_rejects_naive_timestamps() -> None:
    pipeline = DataIngestionPipeline()

    with pytest.raises(DataValidationError):
        pipeline.ingest_market_bars(
            [
                {
                    "instrument": "XAUUSD",
                    "timestamp": datetime(2026, 10, 21, 12, 0),
                    "open": "2600",
                    "high": "2605",
                    "low": "2598",
                    "close": "2602",
                    "available_at": datetime(2026, 10, 21, 12, 1, tzinfo=UTC),
                },
            ],
            source="feed_a",
        )
