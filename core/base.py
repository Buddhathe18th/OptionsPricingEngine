"""Core abstractions for option contracts and pricing engines."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

import numpy as np
from numpy.typing import NDArray


class OptionType(str, Enum):
    """Supported vanilla option types."""

    CALL = "call"
    PUT = "put"


@dataclass(frozen=True, slots=True)
class MarketData:
    """Market inputs for pricing models.

    Parameters
    ----------
    spot:
        Current underlying spot price.
    rate:
        Continuously compounded risk-free rate.
    volatility:
        Annualized volatility.
    maturity:
        Time to maturity in years.
    """

    spot: float
    rate: float
    volatility: float
    maturity: float


@dataclass(frozen=True, slots=True)
class OptionContract(ABC):
    """Abstract option contract interface.

    Parameters
    ----------
    strike:
        Option strike price.
    option_type:
        Call or put indicator.
    """

    strike: float
    option_type: OptionType

    @abstractmethod
    def payoff(self, spot: NDArray[np.float64]) -> NDArray[np.float64]:
        """Compute payoff for given terminal spots."""


@dataclass(frozen=True, slots=True)
class VanillaOption(OptionContract):
    """Vanilla option implementation."""

    def payoff(self, spot: NDArray[np.float64]) -> NDArray[np.float64]:
        intrinsic = np.where(
            self.option_type is OptionType.CALL,
            spot - self.strike,
            self.strike - spot,
        )
        return np.maximum(intrinsic, 0.0)


class PricingEngine(ABC):
    """Strategy interface for pricing engines."""

    @abstractmethod
    def price(self, option: OptionContract, market: MarketData) -> float:
        """Return model price for option and market data."""


class OptionFactory:
    """Factory for constructing option contracts."""

    @staticmethod
    def vanilla(strike: float, option_type: OptionType) -> VanillaOption:
        """Create a vanilla option contract."""

        return VanillaOption(strike=strike, option_type=option_type)
