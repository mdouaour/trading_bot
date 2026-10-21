from trading_core.core.enums import (
    OrderStatus,
    PositionStatus,
    is_valid_order_transition,
    is_valid_position_transition,
)


def test_order_transition_allows_created_to_submitted() -> None:
    assert is_valid_order_transition(OrderStatus.CREATED, OrderStatus.SUBMITTED)


def test_order_transition_disallows_filled_to_submitted() -> None:
    assert not is_valid_order_transition(OrderStatus.FILLED, OrderStatus.SUBMITTED)


def test_position_transition_allows_open_to_closing() -> None:
    assert is_valid_position_transition(PositionStatus.OPEN, PositionStatus.CLOSING)


def test_position_transition_disallows_closed_to_open() -> None:
    assert not is_valid_position_transition(PositionStatus.CLOSED, PositionStatus.OPEN)
