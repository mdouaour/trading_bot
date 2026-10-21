"""Point-in-time snapshot storage with strict no-lookahead semantics."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime

from trading_core.core.types import EconomicEvent, MarketBar


class PointInTimeStore:
    """In-memory point-in-time store used for deterministic decisions and tests."""

    def __init__(self) -> None:
        self._market_bars: dict[str, list[MarketBar]] = defaultdict(list)
        self._economic_events: list[EconomicEvent] = []

    def add_market_bars(self, bars: list[MarketBar]) -> None:
        for bar in bars:
            self._market_bars[bar.instrument].append(bar)

        for instrument in self._market_bars:
            self._market_bars[instrument].sort(key=lambda item: (item.available_at, item.timestamp))

    def add_economic_events(self, events: list[EconomicEvent]) -> None:
        self._economic_events.extend(events)
        self._economic_events.sort(key=lambda item: (item.available_at, item.publication_time))

    def snapshot_market_bars(self, instrument: str, as_of: datetime) -> list[MarketBar]:
        symbol = instrument.upper()
        return [
            bar
            for bar in self._market_bars.get(symbol, [])
            if bar.available_at <= as_of and bar.timestamp <= as_of
        ]

    def latest_market_bar(self, instrument: str, as_of: datetime) -> MarketBar | None:
        bars = self.snapshot_market_bars(instrument, as_of)
        if not bars:
            return None
        return max(bars, key=lambda item: (item.timestamp, item.available_at))

    def snapshot_economic_events(self, as_of: datetime) -> list[EconomicEvent]:
        return [event for event in self._economic_events if event.available_at <= as_of]
