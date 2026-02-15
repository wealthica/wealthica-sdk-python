"""
Wealthica Python SDK - Official Python client for the Wealthica Investment API.

Wealthica is an API for connecting with Canadian financial institutions
and brokerages platforms.
"""

from wealthica.client import Wealthica
from wealthica.exceptions import (
    WealthicaError,
    WealthicaAuthenticationError,
    WealthicaAPIError,
    WealthicaValidationError,
    WealthicaNotFoundError,
    WealthicaRateLimitError,
)

__version__ = "1.0.0"
__all__ = [
    "Wealthica",
    "WealthicaError",
    "WealthicaAuthenticationError",
    "WealthicaAPIError",
    "WealthicaValidationError",
    "WealthicaNotFoundError",
    "WealthicaRateLimitError",
]
