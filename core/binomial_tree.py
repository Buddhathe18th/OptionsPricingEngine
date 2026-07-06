"""Cox-Ross-Rubinstein binomial tree pricing."""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, sqrt

import numpy as np

from core.base import MarketData, OptionContract, PricingEngine


@dataclass(frozen=True, slots=True)
class CRRBinomialEngine(PricingEngine):
    """CRR tree engine for European and American vanilla options.

    Parameters
    ----------
    steps:
        Number of time steps in the tree.
    american:
        Whether to allow early exercise.
    """

    steps: int = 500
    american: bool = True

    def price(self, option: OptionContract, market: MarketData) -> float:
        dt = market.maturity / self.steps
        up = exp(market.volatility * sqrt(dt))
        down = 1.0 / up
        growth = exp(market.rate * dt)
        prob = (growth - down) / (up - down)
        discount = exp(-market.rate * dt)

        nodes = np.arange(self.steps + 1)
        terminal_spots = market.spot * (up ** (self.steps - nodes)) * (down**nodes)
        values = option.payoff(terminal_spots)

        for step in range(self.steps - 1, -1, -1):
            values = discount * (prob * values[:-1] + (1.0 - prob) * values[1:])
            if self.american:
                step_nodes = np.arange(step + 1)
                spots = market.spot * (up ** (step - step_nodes)) * (down**step_nodes)
                values = np.maximum(values, option.payoff(spots))

        return float(values[0])
