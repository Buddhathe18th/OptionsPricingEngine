"""Monte Carlo pricing for geometric Brownian motion dynamics."""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, sqrt

import numpy as np
from numba import njit  # type: ignore[import-untyped]
from numpy.typing import NDArray

from core.base import MarketData, OptionContract, PricingEngine


@njit(nogil=True, fastmath=True)  # type: ignore[misc]
def _terminal_prices(
    spot: float,
    rate: float,
    volatility: float,
    maturity: float,
    paths: int,
    seed: int,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Generate antithetic terminal GBM prices."""

    np.random.seed(seed)
    half = paths // 2
    z = np.random.standard_normal(half)
    drift = (rate - 0.5 * volatility * volatility) * maturity
    diffusion = volatility * sqrt(maturity)
    st_pos = spot * np.exp(drift + diffusion * z)
    st_neg = spot * np.exp(drift - diffusion * z)
    return st_pos, st_neg


@dataclass(frozen=True, slots=True)
class MonteCarloEngine(PricingEngine):
    """Monte Carlo pricing engine.

    Parameters
    ----------
    paths:
        Number of simulated paths. Uses antithetic variates internally.
    seed:
        Random seed for reproducibility.
    use_control_variate:
        Toggle control variate correction based on discounted terminal spot.
    """

    paths: int = 200_000
    seed: int = 7
    use_control_variate: bool = True

    def price(self, option: OptionContract, market: MarketData) -> float:
        st_pos, st_neg = _terminal_prices(
            market.spot,
            market.rate,
            market.volatility,
            market.maturity,
            self.paths,
            self.seed,
        )
        terminal = np.concatenate((st_pos, st_neg))
        payoffs = option.payoff(terminal)
        discount = exp(-market.rate * market.maturity)
        discounted_payoffs = discount * payoffs

        if not self.use_control_variate:
            return float(np.mean(discounted_payoffs))

        control = discount * terminal
        expected_control = market.spot
        covariance = float(np.cov(discounted_payoffs, control, ddof=1)[0, 1])
        control_var = float(np.var(control, ddof=1))
        beta = 0.0 if control_var == 0.0 else covariance / control_var
        estimate = np.mean(discounted_payoffs - beta * (control - expected_control))
        return float(estimate)
