"""Point-in-time aware ingestion pipelines."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal
from typing import Any

from trading_core.core.types import EconomicEvent, MarketBar
from trading_core.data.normalization import normalize_economic_event, normalize_market_bar
from trading_core.data.quality import validate_market_bar_quality


@dataclass(frozen=True)
class IngestionStats:
    input_records: int
    output_records: int
    duplicate_records: int


class DataIngestionPipeline:
    """Ingests and normalizes market and economic data with deduplication."""

    def __init__(
        self,
        *,
        max_spread: Decimal = Decimal("10"),
        max_delay: timedelta = timedelta(days=2),
    ) -> None:
        self._max_spread = max_spread
        self._max_delay = max_delay

    def ingest_market_bars(
        self,
        raw_records: Iterable[Mapping[str, Any]],
        *,
        source: str,
    ) -> tuple[list[MarketBar], IngestionStats]:
        bars: list[MarketBar] = []
        seen: set[tuple[str, str, str, str]] = set()
        duplicates = 0
        total = 0

        for record in raw_records:
            total += 1
            bar = normalize_market_bar(record, source)
            validate_market_bar_quality(bar, max_spread=self._max_spread, max_delay=self._max_delay)

            key = (
                bar.instrument,
                bar.timestamp.isoformat(),
                bar.available_at.isoformat(),
                bar.source,
            )
            if key in seen:
                duplicates += 1
                continue
            seen.add(key)
            bars.append(bar)

        bars.sort(key=lambda item: (item.instrument, item.timestamp, item.available_at))
        return bars, IngestionStats(total, len(bars), duplicates)

    def ingest_economic_events(
        self,
        raw_records: Iterable[Mapping[str, Any]],
        *,
        source: str,
    ) -> tuple[list[EconomicEvent], IngestionStats]:
        events: list[EconomicEvent] = []
        seen: set[tuple[str, str, str]] = set()
        duplicates = 0
        total = 0

        for record in raw_records:
            total += 1
            event = normalize_economic_event(record, source)
            key = (
                event.event_id,
                event.publication_time.isoformat(),
                event.available_at.isoformat(),
            )
            if key in seen:
                duplicates += 1
                continue
            seen.add(key)
            events.append(event)

        events.sort(key=lambda item: (item.event_time, item.publication_time, item.available_at))
        return events, IngestionStats(total, len(events), duplicates)
