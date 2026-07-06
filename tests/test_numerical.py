"""Tests for numerical pricing engines and finite differences."""

from __future__ import annotations

import pytest

from core.binomial_tree import CRRBinomialEngine
from core.black_scholes import BlackScholesEngine
from core.monte_carlo import MonteCarloEngine
from risk.greeks import estimate_greeks


def test_binomial_converges_to_black_scholes(call_option, market_data) -> None:
    bs = BlackScholesEngine().price(call_option, market_data)
    tree = CRRBinomialEngine(steps=1000, american=False).price(call_option, market_data)
    assert tree == pytest.approx(bs, rel=2e-2)


def test_monte_carlo_matches_black_scholes(call_option, market_data) -> None:
    bs = BlackScholesEngine().price(call_option, market_data)
    mc = MonteCarloEngine(paths=100_000, seed=13, use_control_variate=True).price(call_option, market_data)
    assert mc == pytest.approx(bs, rel=2e-2)


def test_finite_difference_greeks_match_analytical(call_option, market_data) -> None:
    engine = BlackScholesEngine()
    analytical = engine.greeks(call_option, market_data)
    numerical = estimate_greeks(engine, call_option, market_data)
    assert numerical.delta == pytest.approx(analytical.delta, rel=2e-3)
    assert numerical.gamma == pytest.approx(analytical.gamma, rel=2e-2)
    assert numerical.vega == pytest.approx(analytical.vega, rel=1e-2)
