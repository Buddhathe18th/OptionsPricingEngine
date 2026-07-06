"""Benchmark script for pricing latency."""

from __future__ import annotations

from timeit import timeit

from core.base import MarketData, OptionFactory, OptionType
from core.black_scholes import BlackScholesEngine


def main() -> None:
    option = OptionFactory.vanilla(strike=100.0, option_type=OptionType.CALL)
    market = MarketData(spot=100.0, rate=0.05, volatility=0.2, maturity=1.0)
    engine = BlackScholesEngine()

    duration = timeit(lambda: engine.price(option, market), number=100_000)
    print(f"Black-Scholes 100k runs: {duration:.4f}s")


if __name__ == "__main__":
    main()
