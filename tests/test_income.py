from decimal import Decimal

import pytest

from core.income import IncomeEngine
from core.lending import LendingPosition
from core.portfolio import Portfolio


def create_portfolio() -> Portfolio:
    return Portfolio(
        lending=LendingPosition(
            collateral_hype=Decimal("10"),
            debt_usdc=Decimal("100"),
        ),
        stable_usdc=Decimal("1000"),
    )


def test_accrue_stable_interest_one_day():
    portfolio = create_portfolio()

    engine = IncomeEngine(
        stable_apr=Decimal("0.06"),
    )

    earned = engine.accrue_stable_interest(portfolio)

    assert earned > Decimal("0")
    assert portfolio.stable_usdc > Decimal("1000")


def test_accrue_stable_interest_one_year():
    portfolio = create_portfolio()

    engine = IncomeEngine(
        stable_apr=Decimal("0.06"),
    )

    engine.accrue_stable_interest(
        portfolio,
        Decimal("365"),
    )

    assert portfolio.stable_usdc > Decimal("1060")


def test_accrue_stable_interest_zero_days():
    portfolio = create_portfolio()

    engine = IncomeEngine(
        stable_apr=Decimal("0.06"),
    )

    earned = engine.accrue_stable_interest(
        portfolio,
        Decimal("0"),
    )

    assert earned == Decimal("0")
    assert portfolio.stable_usdc == Decimal("1000")


def test_accrue_stable_interest_negative_days():
    portfolio = create_portfolio()

    engine = IncomeEngine(
        stable_apr=Decimal("0.06"),
    )

    with pytest.raises(ValueError):
        engine.accrue_stable_interest(
            portfolio,
            Decimal("-1"),
        )
