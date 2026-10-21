"""Signal aggregation logic with explicit NO_TRADE behavior."""

from __future__ import annotations

from trading_core.core.enums import Direction, SignalAction
from trading_core.core.types import AggregationContext, Signal


class WeightedSignalAggregator:
    """Aggregates strategy outputs into BUY/SELL/NO_TRADE decisions."""

    def __init__(self, min_vote_strength: float = 0.6) -> None:
        self._min_vote_strength = min_vote_strength

    def aggregate(self, signals: list[Signal], context: AggregationContext) -> SignalAction:
        if not signals:
            return SignalAction.NO_TRADE

        long_score = 0.0
        short_score = 0.0

        for signal in signals:
            score = signal.confidence * abs(signal.forecast)
            if signal.direction == Direction.LONG:
                long_score += score
            elif signal.direction == Direction.SHORT:
                short_score += score

        if context.current_exposure >= 0.95:
            return SignalAction.NO_TRADE

        if long_score >= self._min_vote_strength and long_score > short_score:
            return SignalAction.BUY
        if short_score >= self._min_vote_strength and short_score > long_score:
            return SignalAction.SELL
        return SignalAction.NO_TRADE
