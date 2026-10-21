from decimal import Decimal

from pytest import MonkeyPatch
from trading_core.core.settings import TradingSettings


def test_settings_defaults() -> None:
    settings = TradingSettings()
    assert settings.environment == "dev"
    assert settings.max_risk_per_trade == Decimal("0.01")
    assert settings.max_positions == 3


def test_settings_env_override(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("TRADING_MAX_RISK_PER_TRADE", "0.02")
    monkeypatch.setenv("TRADING_ENVIRONMENT", "test")

    settings = TradingSettings()

    assert settings.environment == "test"
    assert settings.max_risk_per_trade == Decimal("0.02")
