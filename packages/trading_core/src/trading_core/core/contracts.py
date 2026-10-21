"""Core interfaces that enforce separation between alpha, risk, and execution."""

from __future__ import annotations

from abc import abstractmethod
from decimal import Decimal
from typing import Protocol, runtime_checkable

from trading_core.core.enums import SignalAction
from trading_core.core.types import (
    AccountSnapshot,
    AggregationContext,
    Order,
    OrderRequest,
    Position,
    RiskContext,
    RiskDecision,
    Signal,
    SizingDecision,
    StrategyContext,
    SymbolSpecification,
)


@runtime_checkable
class Strategy(Protocol):
    """Strategy produces signals only and cannot execute orders."""

    @abstractmethod
    def generate_signal(self, context: StrategyContext) -> Signal | None:
        """Generate a signal for a specific point-in-time context."""


@runtime_checkable
class SignalAggregator(Protocol):
    """Aggregates multiple strategy signals into a final action."""

    @abstractmethod
    def aggregate(self, signals: list[Signal], context: AggregationContext) -> SignalAction:
        """Return BUY, SELL, or NO_TRADE."""


@runtime_checkable
class PositionSizer(Protocol):
    """Converts an approved signal into a position size."""

    @abstractmethod
    def size(
        self,
        signal: Signal,
        account: AccountSnapshot,
        symbol: SymbolSpecification,
    ) -> SizingDecision:
        """Compute volatility/risk-aware position size."""


@runtime_checkable
class RiskFirewall(Protocol):
    """Final deterministic guardrail before execution."""

    @abstractmethod
    def evaluate(self, order: OrderRequest, context: RiskContext) -> RiskDecision:
        """Approve, reject, or reduce requested order quantity."""


@runtime_checkable
class BrokerAdapter(Protocol):
    """Broker abstraction; concrete implementation is MT5 in a later phase."""

    @abstractmethod
    async def connect(self) -> None:
        """Initialize broker connectivity."""

    @abstractmethod
    async def health(self) -> bool:
        """Return broker connectivity health state."""

    @abstractmethod
    async def get_account(self) -> AccountSnapshot:
        """Return current account snapshot."""

    @abstractmethod
    async def get_quote(self, instrument: str) -> Decimal:
        """Return current instrument quote or mark price."""

    @abstractmethod
    async def get_positions(self) -> list[Position]:
        """Return currently open positions from broker."""

    @abstractmethod
    async def get_orders(self) -> list[Order]:
        """Return active/recent broker orders for reconciliation."""

    @abstractmethod
    async def submit_order(self, order: OrderRequest) -> Order:
        """Submit an order request to the broker."""

    @abstractmethod
    async def close_position(self, position_id: str, quantity: Decimal | None = None) -> None:
        """Close a position fully or partially."""

    @abstractmethod
    async def reconcile(self) -> None:
        """Trigger broker/internal state reconciliation."""


@runtime_checkable
class OrderManager(Protocol):
    """Order management boundary with idempotent request handling."""

    @abstractmethod
    async def create_order(self, request: OrderRequest, idempotency_key: str) -> Order:
        """Create order record and initialize lifecycle state."""

    @abstractmethod
    async def submit(self, order_id: str) -> Order:
        """Submit existing order through broker adapter."""

    @abstractmethod
    async def cancel(self, order_id: str) -> Order:
        """Cancel an existing live order."""
