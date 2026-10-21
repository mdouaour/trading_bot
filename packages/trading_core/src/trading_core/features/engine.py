"""Deterministic timestamp-safe feature engine."""

from __future__ import annotations

from decimal import Decimal
from math import isfinite, sqrt

from trading_core.core.types import MarketBar


class FeatureEngine:
    """Computes rule-based features from point-in-time market bars."""

    def compute(self, bars: list[MarketBar]) -> dict[str, float]:
        if len(bars) < 2:
            return {}

        sorted_bars = sorted(bars, key=lambda item: (item.timestamp, item.available_at))
        closes = [float(bar.close) for bar in sorted_bars]
        highs = [float(bar.high) for bar in sorted_bars]
        lows = [float(bar.low) for bar in sorted_bars]

        latest = closes[-1]
        prev = closes[-2]
        returns = (latest / prev) - 1 if prev != 0 else 0.0
        log_returns = self._safe_log_ratio(latest, prev)

        sma_5 = self._sma(closes, 5)
        sma_20 = self._sma(closes, 20)
        ema_5 = self._ema(closes, 5)
        ema_20 = self._ema(closes, 20)

        rsi_14 = self._rsi(closes, 14)
        roc_5 = self._roc(closes, 5)
        atr_14 = self._atr(highs, lows, closes, 14)
        rolling_vol_20 = self._rolling_vol(closes, 20)

        trend_slope = self._linear_slope(closes[-20:])
        trend_strength = abs((ema_5 - ema_20) / ema_20) if ema_20 else 0.0

        feature_map = {
            "return_1": returns,
            "log_return_1": log_returns,
            "sma_5": sma_5,
            "sma_20": sma_20,
            "ema_5": ema_5,
            "ema_20": ema_20,
            "trend_slope_20": trend_slope,
            "trend_strength": trend_strength,
            "rsi_14": rsi_14,
            "roc_5": roc_5,
            "atr_14": atr_14,
            "rolling_vol_20": rolling_vol_20,
            "range_position": self._range_position(latest, highs[-20:], lows[-20:]),
        }
        return {k: v for k, v in feature_map.items() if isfinite(v)}

    def _sma(self, values: list[float], period: int) -> float:
        window = values[-period:] if len(values) >= period else values
        return sum(window) / len(window)

    def _ema(self, values: list[float], period: int) -> float:
        alpha = 2 / (period + 1)
        ema = values[0]
        for value in values[1:]:
            ema = alpha * value + (1 - alpha) * ema
        return ema

    def _roc(self, values: list[float], period: int) -> float:
        if len(values) <= period:
            return 0.0
        base = values[-period - 1]
        if base == 0:
            return 0.0
        return (values[-1] / base) - 1

    def _safe_log_ratio(self, latest: float, prev: float) -> float:
        if latest <= 0 or prev <= 0:
            return 0.0
        ratio = Decimal(str(latest)) / Decimal(str(prev))
        return float(ratio.ln())

    def _rolling_vol(self, closes: list[float], period: int) -> float:
        if len(closes) < 2:
            return 0.0
        if len(closes) > period:
            closes = closes[-period:]
        returns = [(closes[i] / closes[i - 1]) - 1 for i in range(1, len(closes)) if closes[i - 1] != 0]
        if not returns:
            return 0.0
        mean = sum(returns) / len(returns)
        variance = sum((value - mean) ** 2 for value in returns) / len(returns)
        return sqrt(variance)

    def _rsi(self, closes: list[float], period: int) -> float:
        if len(closes) <= period:
            return 50.0
        gains: list[float] = []
        losses: list[float] = []
        for index in range(-period, 0):
            delta = closes[index] - closes[index - 1]
            gains.append(max(delta, 0))
            losses.append(abs(min(delta, 0)))

        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def _atr(self, highs: list[float], lows: list[float], closes: list[float], period: int) -> float:
        if len(closes) < 2:
            return 0.0
        true_ranges: list[float] = []
        for index in range(1, len(closes)):
            tr = max(
                highs[index] - lows[index],
                abs(highs[index] - closes[index - 1]),
                abs(lows[index] - closes[index - 1]),
            )
            true_ranges.append(tr)

        if len(true_ranges) > period:
            true_ranges = true_ranges[-period:]
        return sum(true_ranges) / len(true_ranges)

    def _linear_slope(self, values: list[float]) -> float:
        if len(values) < 2:
            return 0.0
        x_values = list(range(len(values)))
        x_mean = sum(x_values) / len(x_values)
        y_mean = sum(values) / len(values)

        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, values, strict=False))
        denominator = sum((x - x_mean) ** 2 for x in x_values)
        if denominator == 0:
            return 0.0
        return numerator / denominator

    def _range_position(self, close: float, highs: list[float], lows: list[float]) -> float:
        highest = max(highs)
        lowest = min(lows)
        if highest == lowest:
            return 0.5
        return (close - lowest) / (highest - lowest)
