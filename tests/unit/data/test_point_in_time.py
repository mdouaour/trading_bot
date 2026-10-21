from __future__ import annotations

from datetime import UTC, datetime

from trading_core.data.ingestion import DataIngestionPipeline
from trading_core.data.point_in_time import PointInTimeStore


def test_snapshot_blocks_lookahead_rows() -> None:
    pipeline = DataIngestionPipeline()
    bars, _stats = pipeline.ingest_market_bars(
        [
            {
                "instrument": "XAUUSD",
                "timestamp": "2026-10-21T10:00:00Z",
                "open": "2600",
                "high": "2602",
                "low": "2599",
                "close": "2601",
                "available_at": "2026-10-21T10:00:01Z",
            },
            {
                "instrument": "XAUUSD",
                "timestamp": "2026-10-21T10:01:00Z",
                "open": "2601",
                "high": "2603",
                "low": "2600",
                "close": "2602",
                "available_at": "2026-10-21T10:06:00Z",
            },
        ],
        source="feed_a",
    )
    store = PointInTimeStore()
    store.add_market_bars(bars)

    snapshot = store.snapshot_market_bars("XAUUSD", datetime(2026, 10, 21, 10, 5, tzinfo=UTC))

    assert len(snapshot) == 1
    assert snapshot[0].timestamp == datetime(2026, 10, 21, 10, 0, tzinfo=UTC)


def test_latest_market_bar_uses_available_data_only() -> None:
    pipeline = DataIngestionPipeline()
    bars, _stats = pipeline.ingest_market_bars(
        [
            {
                "instrument": "XAUUSD",
                "timestamp": "2026-10-21T10:00:00Z",
                "open": "2600",
                "high": "2602",
                "low": "2599",
                "close": "2601",
                "available_at": "2026-10-21T10:00:01Z",
            },
            {
                "instrument": "XAUUSD",
                "timestamp": "2026-10-21T10:01:00Z",
                "open": "2601",
                "high": "2603",
                "low": "2600",
                "close": "2602",
                "available_at": "2026-10-21T10:02:00Z",
            },
        ],
        source="feed_a",
    )
    store = PointInTimeStore()
    store.add_market_bars(bars)

    before_second = store.latest_market_bar("XAUUSD", datetime(2026, 10, 21, 10, 1, 30, tzinfo=UTC))
    after_second = store.latest_market_bar("XAUUSD", datetime(2026, 10, 21, 10, 2, 30, tzinfo=UTC))

    assert before_second is not None
    assert after_second is not None
    assert before_second.timestamp == datetime(2026, 10, 21, 10, 0, tzinfo=UTC)
    assert after_second.timestamp == datetime(2026, 10, 21, 10, 1, tzinfo=UTC)
