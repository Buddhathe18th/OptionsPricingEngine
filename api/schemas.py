"""API request and response schemas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class PriceRequest(BaseModel):
    """Request payload for pricing endpoints."""

    model_config = ConfigDict(extra="forbid")

    spot: float = Field(gt=0)
    strike: float = Field(gt=0)
    rate: float = Field(ge=-1.0, le=1.0)
    volatility: float = Field(gt=0)
    maturity: float = Field(gt=0)
    option_type: str = Field(pattern="^(call|put)$")


class PriceResponse(BaseModel):
    """Pricing result payload."""

    price: float
