from decimal import Decimal

from core.clmm import CLMMPosition
from core.lending import LendingPosition
from core.portfolio import Portfolio


def create_lending() -> LendingPosition:
    return LendingPosition(
        collateral_hype=Decimal("10"),
        debt_usdc=Decimal("100"),
    )


def create_clmm() -> CLMMPosition:
    return CLMMPosition.from_amounts(
        amount0=Decimal("5"),
        amount1=Decimal("100"),
        current_price=Decimal("20"),
        lower_price=Decimal("15"),
        upper_price=Decimal("25"),
    )


def test_total_hype_without_clmm():
    portfolio = Portfolio(
        lending=create_lending(),
        wallet_hype=Decimal("2"),
    )

    assert portfolio.total_hype(Decimal("20")) == Decimal("12")


def test_total_hype_with_clmm():
    clmm = create_clmm()

    expected_hype, _ = clmm.amounts(Decimal("20"))

    portfolio = Portfolio(
        lending=create_lending(),
        clmm=clmm,
        wallet_hype=Decimal("2"),
    )

    assert portfolio.total_hype(Decimal("20")) == (Decimal("12") + expected_hype)


def test_total_usdc_without_clmm():
    portfolio = Portfolio(
        lending=create_lending(),
        stable_usdc=Decimal("300"),
        wallet_usdc=Decimal("25"),
    )

    assert portfolio.total_usdc(Decimal("20")) == Decimal("325")


def test_total_usdc_with_clmm():
    clmm = create_clmm()

    _, expected_usdc = clmm.amounts(Decimal("20"))

    portfolio = Portfolio(
        lending=create_lending(),
        clmm=clmm,
        stable_usdc=Decimal("300"),
        wallet_usdc=Decimal("25"),
    )

    assert portfolio.total_usdc(Decimal("20")) == (Decimal("325") + expected_usdc)


def test_assets_value():
    portfolio = Portfolio(
        lending=create_lending(),
        stable_usdc=Decimal("300"),
        wallet_hype=Decimal("2"),
        wallet_usdc=Decimal("25"),
    )

    expected = Decimal("12") * Decimal("20") + Decimal("325")

    assert portfolio.assets_value(Decimal("20")) == expected


def test_equity():
    portfolio = Portfolio(
        lending=create_lending(),
        stable_usdc=Decimal("300"),
        wallet_hype=Decimal("2"),
        wallet_usdc=Decimal("25"),
    )

    expected_assets = Decimal("12") * Decimal("20") + Decimal("325")

    expected_equity = expected_assets - Decimal("100")

    assert portfolio.equity(Decimal("20")) == expected_equity


def test_leverage():
    portfolio = Portfolio(
        lending=create_lending(),
        stable_usdc=Decimal("300"),
        wallet_hype=Decimal("2"),
        wallet_usdc=Decimal("25"),
    )

    expected_assets = Decimal("12") * Decimal("20") + Decimal("325")

    expected_equity = expected_assets - Decimal("100")

    expected = expected_assets / expected_equity

    assert portfolio.leverage(Decimal("20")) == expected


def test_leverage_empty_portfolio():
    lending = LendingPosition(
        collateral_hype=Decimal("0"),
        debt_usdc=Decimal("0"),
    )

    portfolio = Portfolio(
        lending=lending,
    )

    assert portfolio.leverage(Decimal("20")) == Decimal("0")
