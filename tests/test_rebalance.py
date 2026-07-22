from decimal import Decimal

from core.clmm import CLMMPosition
from core.lending import LendingPosition
from core.portfolio import Portfolio
from core.rebalance import RebalanceEngine


def create_portfolio() -> Portfolio:
    return Portfolio(
        lending=LendingPosition(
            collateral_hype=Decimal("10"),
            debt_usdc=Decimal("100"),
        ),
        clmm=CLMMPosition.from_amounts(
            amount0=Decimal("5"),
            amount1=Decimal("100"),
            current_price=Decimal("20"),
            lower_price=Decimal("18"),
            upper_price=Decimal("22"),
        ),
    )


def test_needs_rebalance_false():
    engine = RebalanceEngine(
        target_hf=Decimal("1.8"),
    )

    assert (
        engine.needs_rebalance(
            create_portfolio(),
            Decimal("20"),
        )
        is False
    )


def test_needs_rebalance_below():
    engine = RebalanceEngine(
        target_hf=Decimal("1.8"),
    )

    assert (
        engine.needs_rebalance(
            create_portfolio(),
            Decimal("17"),
        )
        is True
    )


def test_needs_rebalance_above():
    engine = RebalanceEngine(
        target_hf=Decimal("1.8"),
    )

    assert (
        engine.needs_rebalance(
            create_portfolio(),
            Decimal("23"),
        )
        is True
    )


def test_needs_rebalance_without_clmm():
    portfolio = Portfolio(
        lending=LendingPosition(
            collateral_hype=Decimal("10"),
            debt_usdc=Decimal("100"),
        ),
    )

    engine = RebalanceEngine(
        target_hf=Decimal("1.8"),
    )

    assert (
        engine.needs_rebalance(
            portfolio,
            Decimal("20"),
        )
        is False
    )
