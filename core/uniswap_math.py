"""
Mathematical utilities for Uniswap V3.

This module contains pure mathematical functions used by the CLMM engine.
Functions are deterministic and contain no mutable state.
"""

from __future__ import annotations

from decimal import Decimal, getcontext

getcontext().prec = 50

MIN_PRICE = Decimal("1e-18")
MAX_PRICE = Decimal("1e18")


def _validate_price(price: Decimal) -> None:
    if not price.is_finite():
        raise ValueError("Price must be finite.")

    if price <= 0:
        raise ValueError("Price must be positive.")

    if price < MIN_PRICE or price > MAX_PRICE:
        raise ValueError(f"Price must be between {MIN_PRICE} and {MAX_PRICE}.")


def price_to_sqrt(price: Decimal) -> Decimal:
    _validate_price(price)
    return price.sqrt()


def sqrt_to_price(sqrt_price: Decimal) -> Decimal:
    if not sqrt_price.is_finite():
        raise ValueError("Square root price must be finite.")

    if sqrt_price <= 0:
        raise ValueError("Square root price must be positive.")

    return sqrt_price * sqrt_price


def _validate_range(
    sqrt_lower: Decimal,
    sqrt_upper: Decimal,
) -> None:
    if sqrt_lower <= 0 or sqrt_upper <= 0:
        raise ValueError("Price bounds must be positive.")

    if sqrt_lower >= sqrt_upper:
        raise ValueError("Lower price must be less than upper price.")


def liquidity_from_token0(
    amount0: Decimal,
    sqrt_lower: Decimal,
    sqrt_upper: Decimal,
) -> Decimal:
    """
    Calculate liquidity from token0 amount.

    Assumes current price is at or below the lower bound.
    """
    if amount0 < 0:
        raise ValueError("Amount0 cannot be negative.")

    _validate_range(sqrt_lower, sqrt_upper)

    return amount0 * sqrt_lower * sqrt_upper / (sqrt_upper - sqrt_lower)


def liquidity_from_token1(
    amount1: Decimal,
    sqrt_lower: Decimal,
    sqrt_upper: Decimal,
) -> Decimal:
    """
    Calculate liquidity from token1 amount.

    Assumes current price is at or above the upper bound.
    """
    if amount1 < 0:
        raise ValueError("Amount1 cannot be negative.")

    _validate_range(sqrt_lower, sqrt_upper)

    return amount1 / (sqrt_upper - sqrt_lower)
