"""Append-only event primitives for order and position lifecycles."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import Field

from trading_core.core.enums import OrderStatus, PositionStatus
from trading_core.core.types import UTCModel


class EventBase(UTCModel):
    event_id: UUID = Field(default_factory=uuid4)
    event_time: datetime
    payload: dict[str, Any] = Field(default_factory=dict)


class OrderEvent(EventBase):
    order_id: UUID
    status: OrderStatus


class PositionEvent(EventBase):
    position_id: UUID
    status: PositionStatus
