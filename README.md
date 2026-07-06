# OptionsPricingEngine

A **production-ready quantitative options pricing engine** exposing multiple analytical and numerical pricing models via a secure, validated REST API.

## Features

### Pricing Models
- **Black-Scholes-Merton** – Analytical closed-form pricing and Greeks (delta, gamma, theta, vega, rho, vanna, volga)
- **CRR Binomial Tree** – European and American vanilla option pricing with 500+ time steps
- **Monte Carlo (GBM)** – Risk-neutral simulation with antithetic variates and control variate variance reduction (~100k paths)
- **Heston Stochastic Volatility** – Realistic volatility smile modeling with Euler discretization

### Architecture
- **FastAPI** service with Pydantic validation, comprehensive error handling, and per-client rate limiting (60 req/min)
- **Finite-difference Greeks** module for numerical Greeks estimation across any engine
- **Numba JIT compilation** on Monte Carlo core loop for production performance
- **Strict typing** (mypy strict mode) and security scanning (bandit, flake8)

## Quick Start

### 1. Install Dependencies
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Start the API Server
```powershell
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

The server will start on `http://127.0.0.1:8000`. Check health at `/health`:
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health"
```

### 3. Price an Option

**Using PowerShell (recommended on Windows):**
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/price/black-scholes" -Method Post `
  -Body (ConvertTo-Json @{spot=100; strike=100; rate=0.05; volatility=0.2; maturity=1.0; option_type="call"}) `
  -ContentType "application/json"
```

**Using curl via cmd.exe:**
```powershell
cmd.exe /c curl -s -X POST "http://127.0.0.1:8000/price/black-scholes" -H "Content-Type: application/json" -d "{\"spot\":100,\"strike\":100,\"rate\":0.05,\"volatility\":0.2,\"maturity\":1.0,\"option_type\":\"call\"}"
```

**Expected response:**
```json
{"price": 10.450583572185565}
```

## API Endpoints

All pricing endpoints accept the same JSON request schema:
```json
{
  "spot": 100.0,           // Current underlying price (> 0)
  "strike": 100.0,         // Strike price (> 0)
  "rate": 0.05,            // Risk-free rate in [−1.0, 1.0]
  "volatility": 0.2,       // Annual volatility (> 0)
  "maturity": 1.0,         // Time to expiration in years (> 0)
  "option_type": "call"    // "call" or "put"
}
```

### Pricing Routes

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/price/black-scholes` | `POST` | Fast analytical closed-form pricing (European only) |
| `/price/binomial` | `POST` | Binomial tree pricing (handles American options via early exercise) |
| `/price/monte-carlo` | `POST` | Monte Carlo GBM with control variates (European) |
| `/health` | `GET` | Service health check |

## Testing

Run the full test suite:
```powershell
pytest -v
```

Key test coverage:
- **Analytical:** Black-Scholes accuracy and Greeks
- **Numerical:** Binomial tree convergence, Monte Carlo accuracy vs. Black-Scholes
- **API:** Endpoint validation, malformed request rejection, rate limiting
- **Greeks:** Finite-difference estimators match analytical Greeks

## Project Structure

```
OptionsPricingEngine/
├── api/                      # FastAPI application
│   ├── main.py              # Entry point, middleware (rate limiting, exception handling)
│   ├── routes.py            # Pricing endpoints
│   └── schemas.py           # Pydantic validation schemas
├── core/                     # Pricing engines
│   ├── base.py              # Abstract interfaces, market data, option payoffs
│   ├── black_scholes.py     # Analytical B-S engine with Greeks
│   ├── binomial_tree.py     # CRR binomial tree (European + American)
│   ├── monte_carlo.py       # Monte Carlo GBM with Numba acceleration
│   └── heston.py            # Heston stochastic volatility
├── risk/                     # Risk analytics
│   └── greeks.py            # Finite-difference Greek estimators
├── tests/                    # Test suite
│   ├── test_analytical.py   # Black-Scholes tests
│   ├── test_numerical.py    # Binomial, Monte Carlo, Greeks
│   ├── test_api.py          # API endpoint tests
│   └── conftest.py          # Pytest fixtures
├── scripts/                  # Utility scripts
│   └── benchmark.py          # Performance benchmarks
├── Dockerfile               # Production container
├── pyproject.toml           # Build/test config (mypy strict, pytest)
└── requirements.txt         # Python dependencies

```

## Docker Deployment

Build and run in a container:
```bash
docker build -t options-engine .
docker run -p 8000:8000 options-engine
```

Then access the API at `http://localhost:8000`.

## Development

### Code Quality
- **Type checking:** `mypy --strict`
- **Linting:** `flake8` (100-char lines)
- **Security:** `bandit`
- **Tests:** `pytest` with ~15 unit tests

Run all checks:
```powershell
mypy .
flake8 .
bandit -r core api risk
pytest
```

### Performance Notes
- Monte Carlo engine uses Numba (`@njit`) for ~100× speedup on the path simulation loop
- Binomial tree scales to 500+ steps without memory issues (numpy broadcast arrays)
- All engines are thread-safe; the API handles concurrent requests with in-memory rate-limit windows

## Example Use Cases

1. **Calibration & Risk:** Use the analytical Greeks endpoint for fast delta hedging and Greeks retrieval
2. **Comparison Studies:** Call multiple engines on the same parameters to validate convergence
3. **American Option Pricing:** Only the binomial engine supports early exercise
4. **Vol Surface Exploration:** Batch requests across strikes and maturities for calibration
5. **Stochastic Vol:** Use Heston engine for realistic surface and term structure modeling

## License

Open source. See LICENSE for details.
