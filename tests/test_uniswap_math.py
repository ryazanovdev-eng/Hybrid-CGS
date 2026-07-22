from decimal import Decimal

import pytest

from core.uniswap_math import (
    amount0_from_liquidity,
    amount1_from_liquidity,
    amounts_from_liquidity,
    liquidity_from_amounts,
    liquidity_from_token0,
    liquidity_from_token1,
    price_to_sqrt,
    sqrt_to_price,
)


@pytest.mark.parametrize(
    "price",
    [
        Decimal("0.0001"),
        Decimal("0.01"),
        Decimal("0.1"),
        Decimal("1"),
        Decimal("2"),
        Decimal("10"),
        Decimal("250"),
        Decimal("12345.678"),
    ],
)
def test_roundtrip(price):
    sqrt_price = price_to_sqrt(price)
    restored = sqrt_to_price(sqrt_price)

    assert_decimal_close(restored, price)


@pytest.mark.parametrize(
    "price",
    [
        Decimal("0"),
        Decimal("-1"),
        Decimal("-100"),
    ],
)
def test_invalid_price(price):
    with pytest.raises(ValueError):
        price_to_sqrt(price)


@pytest.mark.parametrize(
    "sqrt_price",
    [
        Decimal("0"),
        Decimal("-1"),
    ],
)
def test_invalid_sqrt(sqrt_price):
    with pytest.raises(ValueError):
        sqrt_to_price(sqrt_price)


def test_known_values():
    assert price_to_sqrt(Decimal("1")) == Decimal("1")
    assert price_to_sqrt(Decimal("4")) == Decimal("2")
    assert sqrt_to_price(Decimal("5")) == Decimal("25")


def assert_decimal_close(
    actual: Decimal,
    expected: Decimal,
    tolerance: Decimal = Decimal("1e-45"),
) -> None:
    assert abs(actual - expected) <= tolerance


def test_liquidity_from_token0_positive():
    lower = Decimal("10").sqrt()
    upper = Decimal("20").sqrt()

    liquidity = liquidity_from_token0(
        Decimal("5"),
        lower,
        upper,
    )

    assert liquidity > 0


def test_liquidity_from_token1_positive():
    lower = Decimal("10").sqrt()
    upper = Decimal("20").sqrt()

    liquidity = liquidity_from_token1(
        Decimal("100"),
        lower,
        upper,
    )

    assert liquidity > 0


def test_zero_amount_returns_zero_liquidity():
    lower = Decimal("10").sqrt()
    upper = Decimal("20").sqrt()

    assert liquidity_from_token0(
        Decimal("0"),
        lower,
        upper,
    ) == Decimal("0")

    assert liquidity_from_token1(
        Decimal("0"),
        lower,
        upper,
    ) == Decimal("0")


def test_negative_amount_raises():
    lower = Decimal("10").sqrt()
    upper = Decimal("20").sqrt()

    with pytest.raises(ValueError):
        liquidity_from_token0(
            Decimal("-1"),
            lower,
            upper,
        )

    with pytest.raises(ValueError):
        liquidity_from_token1(
            Decimal("-1"),
            lower,
            upper,
        )


def test_invalid_range_raises():
    lower = Decimal("10").sqrt()

    with pytest.raises(ValueError):
        liquidity_from_token0(
            Decimal("1"),
            lower,
            lower,
        )

    with pytest.raises(ValueError):
        liquidity_from_token1(
            Decimal("1"),
            lower,
            lower,
        )


def test_liquidity_from_amounts_below_range():
    lower = Decimal("10").sqrt()
    upper = Decimal("20").sqrt()
    price = Decimal("5").sqrt()

    liquidity = liquidity_from_amounts(
        Decimal("5"),
        Decimal("100"),
        price,
        lower,
        upper,
    )

    expected = liquidity_from_token0(
        Decimal("5"),
        lower,
        upper,
    )

    assert liquidity == expected


def test_liquidity_from_amounts_above_range():
    lower = Decimal("10").sqrt()
    upper = Decimal("20").sqrt()
    price = Decimal("30").sqrt()

    liquidity = liquidity_from_amounts(
        Decimal("5"),
        Decimal("100"),
        price,
        lower,
        upper,
    )

    expected = liquidity_from_token1(
        Decimal("100"),
        lower,
        upper,
    )

    assert liquidity == expected


def test_liquidity_from_amounts_inside_range():
    lower = Decimal("10").sqrt()
    upper = Decimal("20").sqrt()
    price = Decimal("15").sqrt()

    liquidity = liquidity_from_amounts(
        Decimal("5"),
        Decimal("100"),
        price,
        lower,
        upper,
    )

    assert liquidity > Decimal("0")


def test_liquidity_from_amounts_negative_amount0():
    lower = Decimal("10").sqrt()
    upper = Decimal("20").sqrt()
    price = Decimal("15").sqrt()

    with pytest.raises(ValueError):
        liquidity_from_amounts(
            Decimal("-1"),
            Decimal("100"),
            price,
            lower,
            upper,
        )


def test_liquidity_from_amounts_negative_amount1():
    lower = Decimal("10").sqrt()
    upper = Decimal("20").sqrt()
    price = Decimal("15").sqrt()

    with pytest.raises(ValueError):
        liquidity_from_amounts(
            Decimal("1"),
            Decimal("-100"),
            price,
            lower,
            upper,
        )


def test_liquidity_from_amounts_invalid_sqrt_price():
    lower = Decimal("10").sqrt()
    upper = Decimal("20").sqrt()

    with pytest.raises(ValueError):
        liquidity_from_amounts(
            Decimal("1"),
            Decimal("100"),
            Decimal("0"),
            lower,
            upper,
        )


def test_liquidity_from_amounts_invalid_range():
    lower = Decimal("10").sqrt()

    with pytest.raises(ValueError):
        liquidity_from_amounts(
            Decimal("1"),
            Decimal("100"),
            Decimal("15").sqrt(),
            lower,
            lower,
        )


def test_amount0_from_liquidity_positive():
    sqrt_price = Decimal("15").sqrt()
    sqrt_upper = Decimal("20").sqrt()

    amount0 = amount0_from_liquidity(
        Decimal("1000"),
        sqrt_price,
        sqrt_upper,
    )

    assert amount0 > Decimal("0")


def test_amount0_from_liquidity_above_range_returns_zero():
    sqrt_price = Decimal("25").sqrt()
    sqrt_upper = Decimal("20").sqrt()

    amount0 = amount0_from_liquidity(
        Decimal("1000"),
        sqrt_price,
        sqrt_upper,
    )

    assert amount0 == Decimal("0")


def test_amount0_from_liquidity_zero_liquidity():
    sqrt_price = Decimal("15").sqrt()
    sqrt_upper = Decimal("20").sqrt()

    amount0 = amount0_from_liquidity(
        Decimal("0"),
        sqrt_price,
        sqrt_upper,
    )

    assert amount0 == Decimal("0")


def test_amount0_from_liquidity_negative_liquidity():
    sqrt_price = Decimal("15").sqrt()
    sqrt_upper = Decimal("20").sqrt()

    with pytest.raises(ValueError):
        amount0_from_liquidity(
            Decimal("-1"),
            sqrt_price,
            sqrt_upper,
        )


def test_amount0_from_liquidity_invalid_sqrt_price():
    sqrt_upper = Decimal("20").sqrt()

    with pytest.raises(ValueError):
        amount0_from_liquidity(
            Decimal("100"),
            Decimal("0"),
            sqrt_upper,
        )


def test_amount0_from_liquidity_invalid_upper():
    sqrt_price = Decimal("15").sqrt()

    with pytest.raises(ValueError):
        amount0_from_liquidity(
            Decimal("100"),
            sqrt_price,
            Decimal("0"),
        )


def test_amount1_from_liquidity_positive():
    sqrt_lower = Decimal("10").sqrt()
    sqrt_price = Decimal("15").sqrt()

    amount1 = amount1_from_liquidity(
        Decimal("1000"),
        sqrt_lower,
        sqrt_price,
    )

    assert amount1 > Decimal("0")


def test_amount1_from_liquidity_below_range_returns_zero():
    sqrt_lower = Decimal("10").sqrt()
    sqrt_price = Decimal("5").sqrt()

    amount1 = amount1_from_liquidity(
        Decimal("1000"),
        sqrt_lower,
        sqrt_price,
    )

    assert amount1 == Decimal("0")


def test_amount1_from_liquidity_zero_liquidity():
    sqrt_lower = Decimal("10").sqrt()
    sqrt_price = Decimal("15").sqrt()

    amount1 = amount1_from_liquidity(
        Decimal("0"),
        sqrt_lower,
        sqrt_price,
    )

    assert amount1 == Decimal("0")


def test_amount1_from_liquidity_negative_liquidity():
    sqrt_lower = Decimal("10").sqrt()
    sqrt_price = Decimal("15").sqrt()

    with pytest.raises(ValueError):
        amount1_from_liquidity(
            Decimal("-1"),
            sqrt_lower,
            sqrt_price,
        )


def test_amount1_from_liquidity_invalid_lower():
    sqrt_price = Decimal("15").sqrt()

    with pytest.raises(ValueError):
        amount1_from_liquidity(
            Decimal("100"),
            Decimal("0"),
            sqrt_price,
        )


def test_amount1_from_liquidity_invalid_sqrt_price():
    sqrt_lower = Decimal("10").sqrt()

    with pytest.raises(ValueError):
        amount1_from_liquidity(
            Decimal("100"),
            sqrt_lower,
            Decimal("0"),
        )


def test_amounts_from_liquidity_below_range():
    lower = Decimal("10").sqrt()
    upper = Decimal("20").sqrt()
    price = Decimal("5").sqrt()

    amount0, amount1 = amounts_from_liquidity(
        Decimal("1000"),
        price,
        lower,
        upper,
    )

    assert amount0 > Decimal("0")
    assert amount1 == Decimal("0")


def test_amounts_from_liquidity_inside_range():
    lower = Decimal("10").sqrt()
    upper = Decimal("20").sqrt()
    price = Decimal("15").sqrt()

    amount0, amount1 = amounts_from_liquidity(
        Decimal("1000"),
        price,
        lower,
        upper,
    )

    assert amount0 > Decimal("0")
    assert amount1 > Decimal("0")


def test_amounts_from_liquidity_above_range():
    lower = Decimal("10").sqrt()
    upper = Decimal("20").sqrt()
    price = Decimal("25").sqrt()

    amount0, amount1 = amounts_from_liquidity(
        Decimal("1000"),
        price,
        lower,
        upper,
    )

    assert amount0 == Decimal("0")
    assert amount1 > Decimal("0")


def test_amounts_from_liquidity_negative_liquidity():
    lower = Decimal("10").sqrt()
    upper = Decimal("20").sqrt()
    price = Decimal("15").sqrt()

    with pytest.raises(ValueError):
        amounts_from_liquidity(
            Decimal("-1"),
            price,
            lower,
            upper,
        )


def test_amounts_from_liquidity_invalid_price():
    lower = Decimal("10").sqrt()
    upper = Decimal("20").sqrt()

    with pytest.raises(ValueError):
        amounts_from_liquidity(
            Decimal("100"),
            Decimal("0"),
            lower,
            upper,
        )
