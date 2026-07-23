from decimal import Decimal

from core.clmm import CLMMPosition

from .test_uniswap_math import assert_decimal_close


def test_sqrt_lower():
    position = CLMMPosition(
        liquidity=Decimal("100"),
        lower_price=Decimal("9"),
        upper_price=Decimal("16"),
    )

    assert position.sqrt_lower == Decimal("3")


def test_sqrt_upper():
    position = CLMMPosition(
        liquidity=Decimal("100"),
        lower_price=Decimal("9"),
        upper_price=Decimal("16"),
    )

    assert position.sqrt_upper == Decimal("4")


def test_in_range():
    position = CLMMPosition(
        liquidity=Decimal("100"),
        lower_price=Decimal("10"),
        upper_price=Decimal("20"),
    )

    assert position.in_range(Decimal("10"))
    assert position.in_range(Decimal("15"))
    assert position.in_range(Decimal("20"))

    assert not position.in_range(Decimal("9"))
    assert not position.in_range(Decimal("21"))


def test_amounts_inside_range():
    position = CLMMPosition(
        liquidity=Decimal("1000"),
        lower_price=Decimal("10"),
        upper_price=Decimal("20"),
    )

    amount0, amount1 = position.amounts(Decimal("15"))

    assert amount0 > Decimal("0")
    assert amount1 > Decimal("0")


def test_value():
    position = CLMMPosition(
        liquidity=Decimal("1000"),
        lower_price=Decimal("10"),
        upper_price=Decimal("20"),
    )

    price = Decimal("15")

    amount0, amount1 = position.amounts(price)

    expected = amount0 * price + amount1

    assert_decimal_close(
        position.value(price),
        expected,
    )


def test_from_amounts():
    position = CLMMPosition.from_amounts(
        amount0=Decimal("5"),
        amount1=Decimal("100"),
        current_price=Decimal("15"),
        lower_price=Decimal("10"),
        upper_price=Decimal("20"),
    )

    assert position.liquidity > Decimal("0")


def test_from_amounts_keeps_range():
    position = CLMMPosition.from_amounts(
        amount0=Decimal("5"),
        amount1=Decimal("100"),
        current_price=Decimal("15"),
        lower_price=Decimal("10"),
        upper_price=Decimal("20"),
    )

    assert position.lower_price == Decimal("10")
    assert position.upper_price == Decimal("20")


def test_from_amounts_restores_used_amounts():
    amount0 = Decimal("5")
    amount1 = Decimal("100")

    position = CLMMPosition.from_amounts(
        amount0=amount0,
        amount1=amount1,
        current_price=Decimal("15"),
        lower_price=Decimal("10"),
        upper_price=Decimal("20"),
    )

    restored0, restored1 = position.amounts(Decimal("15"))

    assert restored0 <= amount0
    assert restored1 <= amount1

    assert restored0 > Decimal("0")
    assert restored1 > Decimal("0")
