"""Heston stochastic volatility model pricing."""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, sqrt

import numpy as np

from core.base import MarketData, OptionContract, PricingEngine


@dataclass(frozen=True, slots=True)
class HestonParams:
    """Heston process parameters."""

    kappa: float
    theta: float
    xi: float
    rho: float
    v0: float


@dataclass(frozen=True, slots=True)
class HestonEngine(PricingEngine):
    """Euler-discretized Heston Monte Carlo engine."""

    params: HestonParams
    steps: int = 252
    paths: int = 50_000
    seed: int = 11

    def price(self, option: OptionContract, market: MarketData) -> float:
        rng = np.random.default_rng(self.seed)
        dt = market.maturity / self.steps

        spot = np.full(self.paths, market.spot, dtype=np.float64)
        var = np.full(self.paths, self.params.v0, dtype=np.float64)

        for _ in range(self.steps):
            z1 = rng.standard_normal(self.paths)
            z2 = rng.standard_normal(self.paths)
            wz = z1
            wv = self.params.rho * z1 + sqrt(1.0 - self.params.rho * self.params.rho) * z2

            var = np.maximum(
                var
                + self.params.kappa * (self.params.theta - var) * dt
                + self.params.xi * np.sqrt(np.maximum(var, 0.0) * dt) * wv,
                0.0,
            )

            spot = spot * np.exp(
                (market.rate - 0.5 * var) * dt + np.sqrt(np.maximum(var, 0.0) * dt) * wz
            )

        payoff = option.payoff(spot)
        return float(exp(-market.rate * market.maturity) * np.mean(payoff))
