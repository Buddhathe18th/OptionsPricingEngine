"""FastAPI entry point with secure defaults."""

from __future__ import annotations

from collections import defaultdict, deque
from time import monotonic
from typing import Awaitable, Callable

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.responses import Response

from api.routes import router

_WINDOW_SECONDS = 60.0
_MAX_REQUESTS_PER_WINDOW = 60
_rate_window: dict[str, deque[float]] = defaultdict(deque)

app = FastAPI(title="Options Pricing Engine", version="0.1.0")
app.include_router(router)


@app.middleware("http")
async def rate_limit(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    client = request.client.host if request.client is not None else "unknown"
    now = monotonic()
    request_times = _rate_window[client]

    while request_times and now - request_times[0] > _WINDOW_SECONDS:
        request_times.popleft()

    if len(request_times) >= _MAX_REQUESTS_PER_WINDOW:
        return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})

    request_times.append(now)
    return await call_next(request)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.exception_handler(Exception)
async def generic_exception_handler(_: Request, __: Exception) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
