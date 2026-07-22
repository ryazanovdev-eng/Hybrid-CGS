import math

import pytest

from core.uniswap_math import (
    price_to_sqrt,
    sqrt_to_price,
)


@pytest.mark.parametrize(
    "price",
    [
        0.0001,
        0.01,
        0.1,
        1,
        2,
        10,
        250,
        12345.678,
    ],
)
def test_roundtrip(price):
    sqrt_price = price_to_sqrt(price)
    restored = sqrt_to_price(sqrt_price)

    assert math.isclose(restored, price, rel_tol=1e-12)


@pytest.mark.parametrize(
    "price",
    [
        0,
        -1,
        -100,
    ],
)
def test_invalid_price(price):
    with pytest.raises(ValueError):
        price_to_sqrt(price)


@pytest.mark.parametrize(
    "sqrt_price",
    [
        0,
        -1,
    ],
)
def test_invalid_sqrt(sqrt_price):
    with pytest.raises(ValueError):
        sqrt_to_price(sqrt_price)


def test_known_values():
    assert price_to_sqrt(1.0) == 1.0
    assert price_to_sqrt(4.0) == 2.0
    assert sqrt_to_price(5.0) == 25.0
