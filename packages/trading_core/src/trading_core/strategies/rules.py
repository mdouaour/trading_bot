"""Deterministic baseline strategies that emit signals only."""

from __future__ import annotations

from trading_core.core.enums import Direction
from trading_core.core.types import Signal, StrategyContext


class BaseRuleStrategy:
    """Base helper for rule strategies."""

    strategy_name: str

    def _signal(
        self,
        context: StrategyContext,
        direction: Direction,
        forecast: float,
        confidence: float,
        reason_codes: list[str],
    ) -> Signal:
        return Signal(
            instrument=context.instrument,
            direction=direction,
            forecast=forecast,
            confidence=confidence,
            strategy=self.strategy_name,
            timestamp=context.as_of,
            reason_codes=reason_codes,
        )


class TrendFollowingStrategy(BaseRuleStrategy):
    strategy_name = "trend_following_v1"

    def generate_signal(self, context: StrategyContext) -> Signal | None:
        features = context.features
        trend_strength = features.get("trend_strength")
        slope = features.get("trend_slope_20")
        if trend_strength is None or slope is None:
            return None

        if slope > 0 and trend_strength > 0.001:
            return self._signal(context, Direction.LONG, min(slope, 1.0), 0.7, ["TREND_UP"])
        if slope < 0 and trend_strength > 0.001:
            return self._signal(context, Direction.SHORT, max(slope, -1.0), 0.7, ["TREND_DOWN"])
        return self._signal(context, Direction.FLAT, 0.0, 0.6, ["TREND_WEAK"])


class MomentumStrategy(BaseRuleStrategy):
    strategy_name = "momentum_v1"

    def generate_signal(self, context: StrategyContext) -> Signal | None:
        roc_5 = context.features.get("roc_5")
        rsi_14 = context.features.get("rsi_14")
        if roc_5 is None or rsi_14 is None:
            return None

        if roc_5 > 0.002 and rsi_14 > 55:
            return self._signal(context, Direction.LONG, roc_5, min(0.9, 0.5 + roc_5 * 20), ["MOMENTUM_UP"])
        if roc_5 < -0.002 and rsi_14 < 45:
            return self._signal(context, Direction.SHORT, roc_5, min(0.9, 0.5 + abs(roc_5) * 20), ["MOMENTUM_DOWN"])
        return self._signal(context, Direction.FLAT, 0.0, 0.55, ["MOMENTUM_NEUTRAL"])


class BreakoutStrategy(BaseRuleStrategy):
    strategy_name = "breakout_v1"

    def generate_signal(self, context: StrategyContext) -> Signal | None:
        range_position = context.features.get("range_position")
        rolling_vol = context.features.get("rolling_vol_20")
        if range_position is None or rolling_vol is None:
            return None

        if range_position > 0.92 and rolling_vol > 0.0005:
            return self._signal(context, Direction.LONG, range_position - 0.5, 0.72, ["BREAKOUT_UP"])
        if range_position < 0.08 and rolling_vol > 0.0005:
            return self._signal(context, Direction.SHORT, 0.5 - range_position, 0.72, ["BREAKOUT_DOWN"])
        return self._signal(context, Direction.FLAT, 0.0, 0.55, ["NO_BREAKOUT"])


class MeanReversionStrategy(BaseRuleStrategy):
    strategy_name = "mean_reversion_v1"

    def generate_signal(self, context: StrategyContext) -> Signal | None:
        rsi_14 = context.features.get("rsi_14")
        if rsi_14 is None:
            return None

        if rsi_14 < 30:
            return self._signal(context, Direction.LONG, (30 - rsi_14) / 100, 0.68, ["OVERSOLD"])
        if rsi_14 > 70:
            return self._signal(context, Direction.SHORT, (rsi_14 - 70) / 100, 0.68, ["OVERBOUGHT"])
        return self._signal(context, Direction.FLAT, 0.0, 0.55, ["RSI_NEUTRAL"])
