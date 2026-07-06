"""Finite-difference Greek estimators."""

from __future__ import annotations

from dataclasses import dataclass

from core.base import MarketData, OptionContract, PricingEngine


@dataclass(frozen=True, slots=True)
class FiniteDifferenceGreeks:
    """Finite-difference estimates for option Greeks."""

    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float


def estimate_greeks(
    engine: PricingEngine,
    option: OptionContract,
    market: MarketData,
    spot_shift: float = 1e-3,
    vol_shift: float = 1e-4,
    rate_shift: float = 1e-4,
    time_shift: float = 1.0 / 365.0,
) -> FiniteDifferenceGreeks:
    """Estimate first and second-order Greeks using central differences."""

    base = engine.price(option, market)

    up_spot = MarketData(market.spot + spot_shift, market.rate, market.volatility, market.maturity)
    dn_spot = MarketData(market.spot - spot_shift, market.rate, market.volatility, market.maturity)
    price_up_spot = engine.price(option, up_spot)
    price_dn_spot = engine.price(option, dn_spot)

    up_vol = MarketData(market.spot, market.rate, market.volatility + vol_shift, market.maturity)
    dn_vol = MarketData(market.spot, market.rate, market.volatility - vol_shift, market.maturity)
    price_up_vol = engine.price(option, up_vol)
    price_dn_vol = engine.price(option, dn_vol)

    up_rate = MarketData(market.spot, market.rate + rate_shift, market.volatility, market.maturity)
    dn_rate = MarketData(market.spot, market.rate - rate_shift, market.volatility, market.maturity)
    price_up_rate = engine.price(option, up_rate)
    price_dn_rate = engine.price(option, dn_rate)

    time_maturity = max(market.maturity - time_shift, 1e-8)
    dn_time = MarketData(market.spot, market.rate, market.volatility, time_maturity)
    price_dn_time = engine.price(option, dn_time)

    delta = (price_up_spot - price_dn_spot) / (2.0 * spot_shift)
    gamma = (price_up_spot - 2.0 * base + price_dn_spot) / (spot_shift * spot_shift)
    vega = (price_up_vol - price_dn_vol) / (2.0 * vol_shift)
    rho = (price_up_rate - price_dn_rate) / (2.0 * rate_shift)
    theta = (price_dn_time - base) / time_shift

    return FiniteDifferenceGreeks(delta=delta, gamma=gamma, theta=theta, vega=vega, rho=rho)
