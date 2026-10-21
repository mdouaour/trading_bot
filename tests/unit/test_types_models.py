from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError
from trading_core.core.enums import Direction, RiskDecisionType
from trading_core.core.types import MarketBar, Quote, RiskDecision, Signal

NOW = datetime(2026, 10, 21, 12, 0, tzinfo=UTC)


def test_quote_rejects_naive_datetime() -> None:
    with pytest.raises(ValidationError):
        Quote(
            instrument="XAUUSD",
            timestamp=datetime(2026, 10, 21, 12, 0),
            bid=Decimal("2600.10"),
            ask=Decimal("2600.50"),
            source="test",
            available_at=NOW,
        )


def test_market_bar_validates_ohlc_consistency() -> None:
    with pytest.raises(ValidationError):
        MarketBar(
            instrument="XAUUSD",
            timestamp=NOW,
            open=Decimal("2600"),
            high=Decimal("2599"),
            low=Decimal("2590"),
            close=Decimal("2598"),
            source="test",
            available_at=NOW,
        )


def test_signal_confidence_range() -> None:
    with pytest.raises(ValidationError):
        Signal(
            signal_id=uuid4(),
            instrument="XAUUSD",
            direction=Direction.LONG,
            forecast=0.01,
            confidence=1.5,
            strategy="trend_v1",
            timestamp=NOW,
        )


def test_risk_decision_reject_requires_zero_approved_quantity() -> None:
    with pytest.raises(ValidationError):
        RiskDecision(
            decision=RiskDecisionType.REJECT,
            requested_quantity=Decimal("1.00"),
            approved_quantity=Decimal("0.10"),
            reason_codes=["DAILY_LOSS_LIMIT"],
            timestamp=NOW,
        )
