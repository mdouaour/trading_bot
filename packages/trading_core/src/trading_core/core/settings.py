"""Typed configuration for risk limits and runtime settings."""

from __future__ import annotations

from decimal import Decimal
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TradingSettings(BaseSettings):
    """Centralized typed settings for deterministic runtime behavior."""

    model_config = SettingsConfigDict(env_prefix="TRADING_", case_sensitive=False, extra="ignore")

    environment: Literal["dev", "test", "prod"] = "dev"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    max_risk_per_trade: Decimal = Field(default=Decimal("0.01"), gt=Decimal("0"), le=Decimal("1"))
    max_daily_loss: Decimal = Field(default=Decimal("0.03"), gt=Decimal("0"), le=Decimal("1"))
    max_drawdown: Decimal = Field(default=Decimal("0.10"), gt=Decimal("0"), le=Decimal("1"))
    max_exposure: Decimal = Field(default=Decimal("0.20"), gt=Decimal("0"), le=Decimal("1"))
    max_leverage: Decimal = Field(default=Decimal("10"), gt=Decimal("0"))
    max_spread: Decimal = Field(default=Decimal("1.50"), gt=Decimal("0"))
    max_slippage: Decimal = Field(default=Decimal("0.50"), gt=Decimal("0"))
    max_positions: int = Field(default=3, ge=1)
    kill_switch: bool = False

    trading_sessions: tuple[str, ...] = ("LONDON", "NEW_YORK", "OVERLAP")
