"""Strategy and signal aggregation modules."""

from trading_core.strategies.aggregation import WeightedSignalAggregator
from trading_core.strategies.rules import (
    BreakoutStrategy,
    MeanReversionStrategy,
    MomentumStrategy,
    TrendFollowingStrategy,
)

__all__ = [
    "BreakoutStrategy",
    "MeanReversionStrategy",
    "MomentumStrategy",
    "TrendFollowingStrategy",
    "WeightedSignalAggregator",
]
