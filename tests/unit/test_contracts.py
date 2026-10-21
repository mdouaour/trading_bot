from __future__ import annotations

from decimal import Decimal

from trading_core.core.contracts import (
    BrokerAdapter,
    OrderManager,
    PositionSizer,
    RiskFirewall,
    SignalAggregator,
    Strategy,
)


class StrategyImpl:
    def generate_signal(self, context: object) -> None:
        return None


class AggregatorImpl:
    def aggregate(self, signals: list[object], context: object) -> str:
        return "NO_TRADE"


class SizerImpl:
    def size(self, signal: object, account: object, symbol: object) -> object:
        return object()


class RiskFirewallImpl:
    def evaluate(self, order: object, context: object) -> object:
        return object()


class BrokerAdapterImpl:
    async def connect(self) -> None:
        return None

    async def health(self) -> bool:
        return True

    async def get_account(self) -> object:
        return object()

    async def get_quote(self, instrument: str) -> Decimal:
        return Decimal("0")

    async def get_positions(self) -> list[object]:
        return []

    async def get_orders(self) -> list[object]:
        return []

    async def submit_order(self, order: object) -> object:
        return object()

    async def close_position(self, position_id: str, quantity: Decimal | None = None) -> None:
        return None

    async def reconcile(self) -> None:
        return None


class OrderManagerImpl:
    async def create_order(self, request: object, idempotency_key: str) -> object:
        return object()

    async def submit(self, order_id: str) -> object:
        return object()

    async def cancel(self, order_id: str) -> object:
        return object()


def test_protocols_are_runtime_checkable() -> None:
    assert isinstance(StrategyImpl(), Strategy)
    assert isinstance(AggregatorImpl(), SignalAggregator)
    assert isinstance(SizerImpl(), PositionSizer)
    assert isinstance(RiskFirewallImpl(), RiskFirewall)
    assert isinstance(BrokerAdapterImpl(), BrokerAdapter)
    assert isinstance(OrderManagerImpl(), OrderManager)
