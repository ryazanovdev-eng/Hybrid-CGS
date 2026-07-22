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


def _validate_sqrt_price(sqrt_price: Decimal) -> None:
    if not sqrt_price.is_finite():
        raise ValueError("Sqrt price must be finite.")

    if sqrt_price <= 0:
        raise ValueError("Sqrt price must be positive.")


def liquidity_from_amounts(
    amount0: Decimal,
    amount1: Decimal,
    sqrt_price: Decimal,
    sqrt_lower: Decimal,
    sqrt_upper: Decimal,
) -> Decimal:
    """
    Calculate the maximum liquidity that can be minted from token amounts.

    Parameters
    ----------
    amount0 : Decimal
        Amount of token0 (HYPE).
    amount1 : Decimal
        Amount of token1 (USDC).
    sqrt_price : Decimal
        Current sqrt(price).
    sqrt_lower : Decimal
        Lower sqrt(price) bound.
    sqrt_upper : Decimal
        Upper sqrt(price) bound.

    Returns
    -------
    Decimal
        Liquidity that can be minted.
    """

    if amount0 < 0:
        raise ValueError("Amount0 cannot be negative.")

    if amount1 < 0:
        raise ValueError("Amount1 cannot be negative.")

    _validate_sqrt_price(sqrt_price)
    _validate_range(sqrt_lower, sqrt_upper)

    # Price is below the range.
    if sqrt_price <= sqrt_lower:
        return liquidity_from_token0(
            amount0,
            sqrt_lower,
            sqrt_upper,
        )

    # Price is above the range.
    if sqrt_price >= sqrt_upper:
        return liquidity_from_token1(
            amount1,
            sqrt_lower,
            sqrt_upper,
        )

    # Price is inside the range.
    liquidity0 = amount0 * sqrt_price * sqrt_upper / (sqrt_upper - sqrt_price)

    liquidity1 = amount1 / (sqrt_price - sqrt_lower)

    return min(liquidity0, liquidity1)
