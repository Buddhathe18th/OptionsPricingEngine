"""API routes for pricing engines."""

from __future__ import annotations

from fastapi import APIRouter

from api.schemas import PriceRequest, PriceResponse
from core.base import MarketData, OptionFactory, OptionType
from core.binomial_tree import CRRBinomialEngine
from core.black_scholes import BlackScholesEngine
from core.monte_carlo import MonteCarloEngine

router = APIRouter(prefix="/price", tags=["pricing"])


@router.post("/black-scholes", response_model=PriceResponse)
def price_black_scholes(request: PriceRequest) -> PriceResponse:
    option = OptionFactory.vanilla(request.strike, OptionType(request.option_type))
    market = MarketData(request.spot, request.rate, request.volatility, request.maturity)
    engine = BlackScholesEngine()
    return PriceResponse(price=engine.price(option, market))


@router.post("/binomial", response_model=PriceResponse)
def price_binomial(request: PriceRequest) -> PriceResponse:
    option = OptionFactory.vanilla(request.strike, OptionType(request.option_type))
    market = MarketData(request.spot, request.rate, request.volatility, request.maturity)
    engine = CRRBinomialEngine(steps=500, american=True)
    return PriceResponse(price=engine.price(option, market))


@router.post("/monte-carlo", response_model=PriceResponse)
def price_monte_carlo(request: PriceRequest) -> PriceResponse:
    option = OptionFactory.vanilla(request.strike, OptionType(request.option_type))
    market = MarketData(request.spot, request.rate, request.volatility, request.maturity)
    engine = MonteCarloEngine(paths=100_000, use_control_variate=True)
    return PriceResponse(price=engine.price(option, market))
