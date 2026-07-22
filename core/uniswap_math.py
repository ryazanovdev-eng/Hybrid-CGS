"""
Mathematical utilities for Uniswap V3.

This module contains pure mathematical functions used by the CLMM engine.
Functions are deterministic and contain no mutable state.
"""

from __future__ import annotations

import math

MIN_PRICE = 1e-18
MAX_PRICE = 1e18


def _validate_price(price: float) -> None:
    """
    Validate price value.

    Parameters
    ----------
    price : float
        Asset price.

    Raises
    ------
    ValueError
        If price is outside supported range.
    """
    if not math.isfinite(price):
        raise ValueError("Price must be finite.")

    if price <= 0:
        raise ValueError("Price must be positive.")

    if price < MIN_PRICE:
        raise ValueError(f"Price must be >= {MIN_PRICE}")

    if price > MAX_PRICE:
        raise ValueError(f"Price must be <= {MAX_PRICE}")


def price_to_sqrt(price: float) -> float:
    """
    Convert price to sqrt(price).

    Parameters
    ----------
    price : float

    Returns
    -------
    float
        sqrt(price)
    """
    _validate_price(price)
    return math.sqrt(price)


def sqrt_to_price(sqrt_price: float) -> float:
    """
    Convert sqrt(price) back to price.

    Parameters
    ----------
    sqrt_price : float

    Returns
    -------
    float
        price
    """
    if not math.isfinite(sqrt_price):
        raise ValueError("sqrt_price must be finite.")

    if sqrt_price <= 0:
        raise ValueError("sqrt_price must be positive.")

    return sqrt_price * sqrt_price
