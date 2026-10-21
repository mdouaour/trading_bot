"""Domain enumerations and deterministic state transitions."""

from __future__ import annotations

from enum import Enum


class Direction(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"
    FLAT = "FLAT"


class SignalAction(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    NO_TRADE = "NO_TRADE"


class RiskDecisionType(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    REDUCE = "REDUCE"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(str, Enum):
    CREATED = "CREATED"
    SUBMITTED = "SUBMITTED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    TIMEOUT = "TIMEOUT"
    FAILED = "FAILED"
    RECONCILIATION_REQUIRED = "RECONCILIATION_REQUIRED"


class PositionStatus(str, Enum):
    OPEN = "OPEN"
    UPDATED = "UPDATED"
    CLOSING = "CLOSING"
    CLOSED = "CLOSED"
    UNKNOWN = "UNKNOWN"


_ORDER_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.CREATED: {OrderStatus.SUBMITTED, OrderStatus.REJECTED, OrderStatus.FAILED},
    OrderStatus.SUBMITTED: {
        OrderStatus.ACKNOWLEDGED,
        OrderStatus.REJECTED,
        OrderStatus.TIMEOUT,
        OrderStatus.FAILED,
        OrderStatus.RECONCILIATION_REQUIRED,
    },
    OrderStatus.ACKNOWLEDGED: {
        OrderStatus.PARTIALLY_FILLED,
        OrderStatus.FILLED,
        OrderStatus.CANCELLED,
        OrderStatus.RECONCILIATION_REQUIRED,
    },
    OrderStatus.PARTIALLY_FILLED: {
        OrderStatus.FILLED,
        OrderStatus.CANCELLED,
        OrderStatus.RECONCILIATION_REQUIRED,
    },
    OrderStatus.FILLED: set(),
    OrderStatus.CANCELLED: set(),
    OrderStatus.REJECTED: set(),
    OrderStatus.TIMEOUT: {OrderStatus.RECONCILIATION_REQUIRED, OrderStatus.FAILED},
    OrderStatus.FAILED: {OrderStatus.RECONCILIATION_REQUIRED},
    OrderStatus.RECONCILIATION_REQUIRED: {
        OrderStatus.PARTIALLY_FILLED,
        OrderStatus.FILLED,
        OrderStatus.CANCELLED,
        OrderStatus.REJECTED,
        OrderStatus.FAILED,
    },
}

_POSITION_TRANSITIONS: dict[PositionStatus, set[PositionStatus]] = {
    PositionStatus.OPEN: {PositionStatus.UPDATED, PositionStatus.CLOSING, PositionStatus.UNKNOWN},
    PositionStatus.UPDATED: {
        PositionStatus.UPDATED,
        PositionStatus.CLOSING,
        PositionStatus.UNKNOWN,
    },
    PositionStatus.CLOSING: {PositionStatus.CLOSED, PositionStatus.UPDATED, PositionStatus.UNKNOWN},
    PositionStatus.CLOSED: set(),
    PositionStatus.UNKNOWN: {
        PositionStatus.UPDATED,
        PositionStatus.CLOSING,
        PositionStatus.CLOSED,
        PositionStatus.UNKNOWN,
    },
}


def is_valid_order_transition(current: OrderStatus, nxt: OrderStatus) -> bool:
    """Return whether an order lifecycle transition is valid."""
    return nxt in _ORDER_TRANSITIONS[current]


def is_valid_position_transition(current: PositionStatus, nxt: PositionStatus) -> bool:
    """Return whether a position lifecycle transition is valid."""
    return nxt in _POSITION_TRANSITIONS[current]
