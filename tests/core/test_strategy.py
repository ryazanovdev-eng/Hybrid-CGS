from decimal import Decimal

import pytest

from core.strategy import Allocation, HybridCGSStrategy
from tests.core.test_rebalance import create_portfolio


def test_allocate_zero_stable():
    portfolio = create_portfolio()

    portfolio.wallet_hype = Decimal("5")
    portfolio.wallet_usdc = Decimal("100")

    strategy = HybridCGSStrategy(
        stable_ratio=Decimal("0"),
    )

    allocation = strategy.allocate(
        portfolio,
        Decimal("20"),
    )

    assert allocation == Allocation(
        clmm_hype=Decimal("5"),
        clmm_usdc=Decimal("100"),
        stable_usdc=Decimal("0"),
    )


def test_allocate_half_stable():
    portfolio = create_portfolio()

    portfolio.wallet_hype = Decimal("5")
    portfolio.wallet_usdc = Decimal("100")

    strategy = HybridCGSStrategy(
        stable_ratio=Decimal("0.5"),
    )

    allocation = strategy.allocate(
        portfolio,
        Decimal("20"),
    )

    assert allocation == Allocation(
        clmm_hype=Decimal("5"),
        clmm_usdc=Decimal("50"),
        stable_usdc=Decimal("50"),
    )


def test_allocate_all_stable():
    portfolio = create_portfolio()

    portfolio.wallet_hype = Decimal("5")
    portfolio.wallet_usdc = Decimal("100")

    strategy = HybridCGSStrategy(
        stable_ratio=Decimal("1"),
    )

    allocation = strategy.allocate(
        portfolio,
        Decimal("20"),
    )

    assert allocation == Allocation(
        clmm_hype=Decimal("5"),
        clmm_usdc=Decimal("0"),
        stable_usdc=Decimal("100"),
    )


@pytest.mark.parametrize(
    "ratio",
    [
        Decimal("-0.1"),
        Decimal("1.1"),
    ],
)
def test_allocate_invalid_ratio(ratio: Decimal):
    portfolio = create_portfolio()

    strategy = HybridCGSStrategy(
        stable_ratio=ratio,
    )

    with pytest.raises(ValueError):
        strategy.allocate(
            portfolio,
            Decimal("20"),
        )
