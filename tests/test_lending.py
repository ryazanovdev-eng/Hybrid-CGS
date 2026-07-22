from decimal import Decimal

import pytest

from core.lending import LendingPosition


def test_collateral_value():
    lending = LendingPosition(
        collateral_hype=Decimal("10"),
        debt_usdc=Decimal("100"),
    )

    assert lending.collateral_value(Decimal("20")) == Decimal("200")


def test_ltv():
    lending = LendingPosition(
        collateral_hype=Decimal("10"),
        debt_usdc=Decimal("100"),
    )

    # collateral = 200
    # debt = 100
    # LTV = 0.5

    assert lending.ltv(Decimal("20")) == Decimal("0.5")


def test_ltv_zero_collateral():
    lending = LendingPosition(
        collateral_hype=Decimal("0"),
        debt_usdc=Decimal("100"),
    )

    assert lending.ltv(Decimal("20")) == Decimal("0")


def test_health_factor():
    lending = LendingPosition(
        collateral_hype=Decimal("10"),
        debt_usdc=Decimal("100"),
    )

    hf = lending.health_factor(Decimal("20"))

    assert hf == Decimal("1.48")


def test_health_factor_no_debt():
    lending = LendingPosition(
        collateral_hype=Decimal("10"),
        debt_usdc=Decimal("0"),
    )

    assert lending.health_factor(Decimal("20")) == Decimal("Infinity")


def test_borrow_capacity():
    lending = LendingPosition(
        collateral_hype=Decimal("10"),
        debt_usdc=Decimal("0"),
    )

    assert lending.borrow_capacity(Decimal("20")) == Decimal("148")


def test_deposit_collateral():
    lending = LendingPosition(
        collateral_hype=Decimal("10"),
        debt_usdc=Decimal("100"),
    )

    lending.deposit_collateral(Decimal("5"))

    assert lending.collateral_hype == Decimal("15")


def test_withdraw_collateral():
    lending = LendingPosition(
        collateral_hype=Decimal("10"),
        debt_usdc=Decimal("100"),
    )

    lending.withdraw_collateral(Decimal("3"))

    assert lending.collateral_hype == Decimal("7")


def test_borrow():
    lending = LendingPosition(
        collateral_hype=Decimal("10"),
        debt_usdc=Decimal("100"),
    )

    lending.borrow(Decimal("50"))

    assert lending.debt_usdc == Decimal("150")


def test_repay():
    lending = LendingPosition(
        collateral_hype=Decimal("10"),
        debt_usdc=Decimal("100"),
    )

    lending.repay(Decimal("40"))

    assert lending.debt_usdc == Decimal("60")


def test_accrue_interest_one_day():
    lending = LendingPosition(
        collateral_hype=Decimal("100"),
        debt_usdc=Decimal("100"),
    )

    lending.accrue_interest()

    assert lending.collateral_hype > Decimal("100")
    assert lending.debt_usdc > Decimal("100")


def test_accrue_interest_one_year():
    lending = LendingPosition(
        collateral_hype=Decimal("100"),
        debt_usdc=Decimal("100"),
    )

    lending.accrue_interest(Decimal("365"))

    assert lending.collateral_hype > Decimal("101.9")
    assert lending.debt_usdc > Decimal("104.5")


def test_accrue_interest_zero_days():
    lending = LendingPosition(
        collateral_hype=Decimal("100"),
        debt_usdc=Decimal("100"),
    )

    lending.accrue_interest(Decimal("0"))

    assert lending.collateral_hype == Decimal("100")
    assert lending.debt_usdc == Decimal("100")


def test_accrue_interest_negative_days():
    lending = LendingPosition(
        collateral_hype=Decimal("100"),
        debt_usdc=Decimal("100"),
    )

    with pytest.raises(ValueError):
        lending.accrue_interest(Decimal("-1"))
