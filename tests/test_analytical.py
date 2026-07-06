"""Tests for analytical pricing and Greeks."""

from __future__ import annotations

from math import exp

import pytest

from core.black_scholes import BlackScholesEngine


@pytest.mark.parametrize("expected", [10.4506])
def test_black_scholes_call_price(call_option, market_data, expected: float) -> None:
    engine = BlackScholesEngine()
    price = engine.price(call_option, market_data)
    assert price == pytest.approx(expected, rel=1e-3)


def test_put_call_parity(call_option, put_option, market_data) -> None:
    engine = BlackScholesEngine()
    call = engine.price(call_option, market_data)
    put = engine.price(put_option, market_data)
    lhs = call - put
    rhs = market_data.spot - call_option.strike * exp(-market_data.rate * market_data.maturity)
    assert lhs == pytest.approx(rhs, rel=1e-6)


def test_analytical_greeks_alignment(call_option, market_data) -> None:
    engine = BlackScholesEngine()
    result = engine.greeks(call_option, market_data)
    assert 0.0 < result.delta < 1.0
    assert result.gamma > 0.0
    assert result.vega > 0.0
