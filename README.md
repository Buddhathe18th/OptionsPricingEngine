# OptionsPricingEngine

Production-oriented quantitative options pricing engine with:

- Black-Scholes-Merton analytical pricing and closed-form Greeks
- CRR binomial tree pricing for European and American options
- Monte Carlo GBM pricing with antithetic and control variate variance reduction
- Heston stochastic volatility Monte Carlo engine
- FastAPI service with validation, rate limiting, and safe error handling
- CI pipeline running flake8, mypy, bandit, and pytest
