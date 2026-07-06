"""Shared test fixtures."""

from __future__ import annotations

import pytest

from core.base import MarketData, OptionFactory, OptionType


@pytest.fixture
def market_data() -> MarketData:
    return MarketData(spot=100.0, rate=0.05, volatility=0.2, maturity=1.0)


@pytest.fixture
def call_option():
    return OptionFactory.vanilla(strike=100.0, option_type=OptionType.CALL)


@pytest.fixture
def put_option():
    return OptionFactory.vanilla(strike=100.0, option_type=OptionType.PUT)
