"""Black-Scholes-Merton analytical pricing and Greeks."""

from __future__ import annotations

from dataclasses import dataclass
from math import erf, exp, log, pi, sqrt

from core.base import MarketData, OptionContract, OptionType, PricingEngine


def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + erf(x / sqrt(2.0)))


def _norm_pdf(x: float) -> float:
    return exp(-0.5 * x * x) / sqrt(2.0 * pi)


@dataclass(frozen=True, slots=True)
class BlackScholesResult:
    """Price and analytical Greeks for Black-Scholes model."""

    price: float
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float
    vanna: float
    volga: float


class BlackScholesEngine(PricingEngine):
    """Black-Scholes-Merton pricing strategy."""

    def _d1_d2(self, option: OptionContract, market: MarketData) -> tuple[float, float]:
        vol_sqrt_t = market.volatility * sqrt(market.maturity)
        d1 = (
            log(market.spot / option.strike)
            + (market.rate + 0.5 * market.volatility * market.volatility) * market.maturity
        ) / vol_sqrt_t
        d2 = d1 - vol_sqrt_t
        return d1, d2

    def greeks(self, option: OptionContract, market: MarketData) -> BlackScholesResult:
        """Compute Black-Scholes price and Greeks."""

        d1, d2 = self._d1_d2(option, market)
        nd1 = _norm_pdf(d1)
        cdf_d1 = _norm_cdf(d1)
        cdf_d2 = _norm_cdf(d2)
        discount = exp(-market.rate * market.maturity)
        sqrt_t = sqrt(market.maturity)

        if option.option_type is OptionType.CALL:
            price = market.spot * cdf_d1 - option.strike * discount * cdf_d2
            delta = cdf_d1
            theta = (
                -(market.spot * nd1 * market.volatility) / (2.0 * sqrt_t)
                - market.rate * option.strike * discount * cdf_d2
            )
            rho = option.strike * market.maturity * discount * cdf_d2
        else:
            cdf_md1 = _norm_cdf(-d1)
            cdf_md2 = _norm_cdf(-d2)
            price = option.strike * discount * cdf_md2 - market.spot * cdf_md1
            delta = cdf_d1 - 1.0
            theta = (
                -(market.spot * nd1 * market.volatility) / (2.0 * sqrt_t)
                + market.rate * option.strike * discount * cdf_md2
            )
            rho = -option.strike * market.maturity * discount * cdf_md2

        gamma = nd1 / (market.spot * market.volatility * sqrt_t)
        vega = market.spot * sqrt_t * nd1
        vanna = vega * (1.0 - d1 / (market.volatility * sqrt_t)) / market.spot
        volga = vega * d1 * d2 / market.volatility

        return BlackScholesResult(
            price=price,
            delta=delta,
            gamma=gamma,
            theta=theta,
            vega=vega,
            rho=rho,
            vanna=vanna,
            volga=volga,
        )

    def price(self, option: OptionContract, market: MarketData) -> float:
        return self.greeks(option, market).price
