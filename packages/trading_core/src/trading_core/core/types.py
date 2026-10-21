"""Canonical Phase 1 domain models."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from trading_core.core.enums import (
    Direction,
    OrderSide,
    OrderStatus,
    OrderType,
    PositionStatus,
    RiskDecisionType,
)


class UTCModel(BaseModel):
    """Base model enforcing timezone-aware UTC datetimes."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    @field_validator("*", mode="before")
    @classmethod
    def _normalize_datetime_fields(cls, value: Any) -> Any:
        if isinstance(value, datetime):
            if value.tzinfo is None or value.utcoffset() is None:
                raise ValueError("datetime fields must be timezone-aware")
            return value.astimezone(UTC)
        return value


class Quote(UTCModel):
    instrument: str = Field(min_length=1)
    timestamp: datetime
    bid: Decimal = Field(gt=0)
    ask: Decimal = Field(gt=0)
    source: str = Field(min_length=1)
    available_at: datetime

    @property
    def spread(self) -> Decimal:
        return self.ask - self.bid

    @model_validator(mode="after")
    def validate_bid_ask(self) -> Quote:
        if self.ask < self.bid:
            msg = "ask must be greater than or equal to bid"
            raise ValueError(msg)
        if self.available_at < self.timestamp:
            msg = "available_at must be >= timestamp"
            raise ValueError(msg)
        return self


class MarketBar(UTCModel):
    instrument: str = Field(min_length=1)
    timestamp: datetime
    open: Decimal = Field(gt=0)
    high: Decimal = Field(gt=0)
    low: Decimal = Field(gt=0)
    close: Decimal = Field(gt=0)
    volume: Decimal | None = Field(default=None, ge=0)
    bid: Decimal | None = Field(default=None, gt=0)
    ask: Decimal | None = Field(default=None, gt=0)
    source: str = Field(min_length=1)
    available_at: datetime

    @model_validator(mode="after")
    def validate_ohlc(self) -> MarketBar:
        if self.high < max(self.open, self.close) or self.low > min(self.open, self.close):
            msg = "OHLC values are inconsistent"
            raise ValueError(msg)
        if self.high < self.low:
            msg = "high must be greater than or equal to low"
            raise ValueError(msg)
        if self.bid is not None and self.ask is not None and self.ask < self.bid:
            msg = "ask must be greater than or equal to bid"
            raise ValueError(msg)
        if self.available_at < self.timestamp:
            msg = "available_at must be >= timestamp"
            raise ValueError(msg)
        return self


class EconomicEvent(UTCModel):
    event_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    instrument: str | None = None
    event_time: datetime
    publication_time: datetime
    revision_time: datetime | None = None
    actual: float | None = None
    forecast: float | None = None
    previous: float | None = None
    source: str = Field(min_length=1)
    available_at: datetime

    @model_validator(mode="after")
    def validate_temporal_order(self) -> EconomicEvent:
        if self.publication_time < self.event_time:
            msg = "publication_time must be >= event_time"
            raise ValueError(msg)
        if self.revision_time is not None and self.revision_time < self.publication_time:
            msg = "revision_time must be >= publication_time"
            raise ValueError(msg)
        if self.available_at < self.publication_time:
            msg = "available_at must be >= publication_time"
            raise ValueError(msg)
        return self


class Signal(UTCModel):
    signal_id: UUID = Field(default_factory=uuid4)
    instrument: str = Field(min_length=1)
    direction: Direction
    forecast: float
    confidence: float = Field(ge=0, le=1)
    expected_return: float | None = None
    expected_volatility: float | None = Field(default=None, ge=0)
    regime: str | None = None
    strategy: str = Field(min_length=1)
    model_version: str | None = None
    features_version: str | None = None
    timestamp: datetime
    reason_codes: list[str] = Field(default_factory=list)


class RiskDecision(UTCModel):
    decision: RiskDecisionType
    requested_quantity: Decimal = Field(gt=0)
    approved_quantity: Decimal = Field(ge=0)
    reason_codes: list[str] = Field(default_factory=list)
    timestamp: datetime

    @model_validator(mode="after")
    def validate_decision(self) -> RiskDecision:
        if self.decision == RiskDecisionType.REJECT and self.approved_quantity != Decimal("0"):
            msg = "REJECT decisions must have approved_quantity == 0"
            raise ValueError(msg)
        if self.decision == RiskDecisionType.APPROVE and self.approved_quantity <= Decimal("0"):
            msg = "APPROVE decisions must have approved_quantity > 0"
            raise ValueError(msg)
        if self.approved_quantity > self.requested_quantity:
            msg = "approved_quantity cannot exceed requested_quantity"
            raise ValueError(msg)
        return self


class OrderRequest(UTCModel):
    instrument: str = Field(min_length=1)
    side: OrderSide
    order_type: OrderType
    quantity: Decimal = Field(gt=0)
    price: Decimal | None = Field(default=None, gt=0)
    stop_loss: Decimal | None = Field(default=None, gt=0)
    take_profit: Decimal | None = Field(default=None, gt=0)
    signal_id: UUID
    strategy: str = Field(min_length=1)
    requested_at: datetime


class Order(UTCModel):
    order_id: UUID = Field(default_factory=uuid4)
    idempotency_key: str = Field(min_length=1)
    instrument: str = Field(min_length=1)
    side: OrderSide
    order_type: OrderType
    quantity: Decimal = Field(gt=0)
    price: Decimal | None = Field(default=None, gt=0)
    stop_loss: Decimal | None = Field(default=None, gt=0)
    take_profit: Decimal | None = Field(default=None, gt=0)
    strategy: str = Field(min_length=1)
    signal_id: UUID
    status: OrderStatus = OrderStatus.CREATED
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="after")
    def validate_timestamps(self) -> Order:
        if self.updated_at < self.created_at:
            msg = "updated_at must be >= created_at"
            raise ValueError(msg)
        return self


class Position(UTCModel):
    position_id: UUID = Field(default_factory=uuid4)
    instrument: str = Field(min_length=1)
    side: OrderSide
    quantity: Decimal = Field(gt=0)
    entry_price: Decimal = Field(gt=0)
    status: PositionStatus = PositionStatus.OPEN
    opened_at: datetime
    updated_at: datetime
    closed_at: datetime | None = None

    @model_validator(mode="after")
    def validate_timestamps(self) -> Position:
        if self.updated_at < self.opened_at:
            msg = "updated_at must be >= opened_at"
            raise ValueError(msg)
        if self.closed_at is not None and self.closed_at < self.opened_at:
            msg = "closed_at must be >= opened_at"
            raise ValueError(msg)
        return self


class StrategyContext(UTCModel):
    instrument: str = Field(min_length=1)
    as_of: datetime
    market_bar: MarketBar | None = None
    quote: Quote | None = None
    features: dict[str, float] = Field(default_factory=dict)


class AggregationContext(UTCModel):
    instrument: str = Field(min_length=1)
    as_of: datetime
    current_exposure: Decimal = Field(ge=0)


class AccountSnapshot(UTCModel):
    account_id: str = Field(min_length=1)
    equity: Decimal = Field(gt=0)
    balance: Decimal = Field(gt=0)
    leverage: Decimal = Field(gt=0)
    timestamp: datetime


class SymbolSpecification(UTCModel):
    instrument: str = Field(min_length=1)
    contract_size: Decimal = Field(gt=0)
    min_lot: Decimal = Field(gt=0)
    lot_step: Decimal = Field(gt=0)
    tick_size: Decimal = Field(gt=0)


class SizingDecision(UTCModel):
    requested_quantity: Decimal = Field(gt=0)
    sized_quantity: Decimal = Field(ge=0)
    reason_codes: list[str] = Field(default_factory=list)
    timestamp: datetime

    @model_validator(mode="after")
    def validate_size(self) -> SizingDecision:
        if self.sized_quantity > self.requested_quantity:
            msg = "sized_quantity cannot exceed requested_quantity"
            raise ValueError(msg)
        return self


class RiskContext(UTCModel):
    account: AccountSnapshot
    symbol: SymbolSpecification
    open_positions: list[Position] = Field(default_factory=list)
    pending_orders: list[Order] = Field(default_factory=list)
    as_of: datetime
