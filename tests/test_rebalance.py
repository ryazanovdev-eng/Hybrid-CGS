from decimal import Decimal

import pytest

from core.clmm import CLMMPosition
from core.lending import LendingPosition
from core.portfolio import Portfolio
from core.rebalance import RebalanceEngine
from core.strategy import HybridCGSStrategy


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
        strategy=HybridCGSStrategy(
            stable_ratio=Decimal("0.3"),
        ),
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
        strategy=HybridCGSStrategy(
            stable_ratio=Decimal("0.3"),
        ),
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
        strategy=HybridCGSStrategy(
            stable_ratio=Decimal("0.3"),
        ),
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
        strategy=HybridCGSStrategy(
            stable_ratio=Decimal("0.3"),
        ),
    )

    assert (
        engine.needs_rebalance(
            portfolio,
            Decimal("20"),
        )
        is False
    )


def test_close_position():
    portfolio = create_portfolio()

    expected_hype, expected_usdc = portfolio.clmm.amounts(Decimal("20"))

    engine = RebalanceEngine(
        target_hf=Decimal("1.8"),
        strategy=HybridCGSStrategy(
            stable_ratio=Decimal("0.3"),
        ),
    )

    engine.close_position(
        portfolio,
        Decimal("20"),
    )

    assert portfolio.clmm is None
    assert portfolio.wallet_hype == expected_hype
    assert portfolio.wallet_usdc == expected_usdc


def test_close_position_without_clmm():
    portfolio = Portfolio(
        lending=LendingPosition(
            collateral_hype=Decimal("10"),
            debt_usdc=Decimal("100"),
        ),
    )

    engine = RebalanceEngine(
        target_hf=Decimal("1.8"),
        strategy=HybridCGSStrategy(
            stable_ratio=Decimal("0.3"),
        ),
    )

    engine.close_position(
        portfolio,
        Decimal("20"),
    )

    assert portfolio.clmm is None
    assert portfolio.wallet_hype == Decimal("0")
    assert portfolio.wallet_usdc == Decimal("0")


def test_close_position_does_not_modify_lending():
    portfolio = create_portfolio()

    collateral = portfolio.lending.collateral_hype
    debt = portfolio.lending.debt_usdc

    engine = RebalanceEngine(
        target_hf=Decimal("1.8"),
        strategy=HybridCGSStrategy(
            stable_ratio=Decimal("0.3"),
        ),
    )

    engine.close_position(
        portfolio,
        Decimal("20"),
    )

    assert portfolio.lending.collateral_hype == collateral
    assert portfolio.lending.debt_usdc == debt


def test_repay_debt_full():
    portfolio = create_portfolio()
    portfolio.wallet_usdc = Decimal("100")

    engine = RebalanceEngine(
        target_hf=Decimal("1.8"),
        strategy=HybridCGSStrategy(
            stable_ratio=Decimal("0.3"),
        ),
    )

    repaid = engine.repay_debt(
        portfolio,
        Decimal("100"),
    )

    assert repaid == Decimal("100")
    assert portfolio.wallet_usdc == Decimal("0")
    assert portfolio.lending.debt_usdc == Decimal("0")


def test_repay_debt_partial():
    portfolio = create_portfolio()
    portfolio.wallet_usdc = Decimal("50")

    engine = RebalanceEngine(
        target_hf=Decimal("1.8"),
        strategy=HybridCGSStrategy(
            stable_ratio=Decimal("0.3"),
        ),
    )

    repaid = engine.repay_debt(
        portfolio,
        Decimal("50"),
    )

    assert repaid == Decimal("50")
    assert portfolio.wallet_usdc == Decimal("0")
    assert portfolio.lending.debt_usdc == Decimal("50")


def test_repay_debt_more_than_debt():
    portfolio = create_portfolio()
    portfolio.wallet_usdc = Decimal("200")

    engine = RebalanceEngine(
        target_hf=Decimal("1.8"),
        strategy=HybridCGSStrategy(
            stable_ratio=Decimal("0.3"),
        ),
    )

    repaid = engine.repay_debt(
        portfolio,
        Decimal("200"),
    )

    assert repaid == Decimal("100")
    assert portfolio.wallet_usdc == Decimal("100")
    assert portfolio.lending.debt_usdc == Decimal("0")


def test_repay_debt_limited_by_wallet():
    portfolio = create_portfolio()
    portfolio.wallet_usdc = Decimal("30")

    engine = RebalanceEngine(
        target_hf=Decimal("1.8"),
        strategy=HybridCGSStrategy(
            stable_ratio=Decimal("0.3"),
        ),
    )

    repaid = engine.repay_debt(
        portfolio,
        Decimal("100"),
    )

    assert repaid == Decimal("30")
    assert portfolio.wallet_usdc == Decimal("0")
    assert portfolio.lending.debt_usdc == Decimal("70")


def test_repay_debt_zero():
    portfolio = create_portfolio()

    engine = RebalanceEngine(
        target_hf=Decimal("1.8"),
        strategy=HybridCGSStrategy(
            stable_ratio=Decimal("0.3"),
        ),
    )

    repaid = engine.repay_debt(
        portfolio,
        Decimal("0"),
    )

    assert repaid == Decimal("0")
    assert portfolio.lending.debt_usdc == Decimal("100")


def test_repay_debt_negative():
    portfolio = create_portfolio()

    engine = RebalanceEngine(
        target_hf=Decimal("1.8"),
        strategy=HybridCGSStrategy(
            stable_ratio=Decimal("0.3"),
        ),
    )

    with pytest.raises(ValueError):
        engine.repay_debt(
            portfolio,
            Decimal("-1"),
        )


def test_borrow_to_target_hf():
    portfolio = create_portfolio()

    portfolio.lending.debt_usdc = Decimal("80")

    engine = RebalanceEngine(
        target_hf=Decimal("1.8"),
        strategy=HybridCGSStrategy(
            stable_ratio=Decimal("0.3"),
        ),
    )

    borrowed = engine.borrow_to_target_hf(
        portfolio,
        Decimal("20"),
    )

    assert borrowed > Decimal("0")
    assert portfolio.wallet_usdc == borrowed
    assert portfolio.lending.debt_usdc == Decimal("80") + borrowed
    assert portfolio.lending.health_factor(Decimal("20")) == Decimal("1.8")


def test_borrow_to_target_hf_already_at_target():
    portfolio = create_portfolio()

    portfolio.lending.debt_usdc = (
        portfolio.lending.collateral_value(Decimal("20"))
        * portfolio.lending.liquidation_threshold
        / Decimal("1.8")
    )

    engine = RebalanceEngine(
        target_hf=Decimal("1.8"),
        strategy=HybridCGSStrategy(
            stable_ratio=Decimal("0.3"),
        ),
    )

    borrowed = engine.borrow_to_target_hf(
        portfolio,
        Decimal("20"),
    )

    assert borrowed == Decimal("0")
    assert portfolio.wallet_usdc == Decimal("0")


def test_borrow_to_target_hf_above_target():
    portfolio = create_portfolio()

    portfolio.lending.debt_usdc = Decimal("101")

    engine = RebalanceEngine(
        target_hf=Decimal("1.8"),
        strategy=HybridCGSStrategy(
            stable_ratio=Decimal("0.3"),
        ),
    )

    borrowed = engine.borrow_to_target_hf(
        portfolio,
        Decimal("20"),
    )

    assert borrowed == Decimal("0")
    assert portfolio.wallet_usdc == Decimal("0")
    assert portfolio.lending.debt_usdc == Decimal("101")


def test_borrow_to_target_hf_adds_to_wallet():
    portfolio = create_portfolio()
    portfolio.wallet_usdc = Decimal("15")

    engine = RebalanceEngine(
        target_hf=Decimal("1.8"),
        strategy=HybridCGSStrategy(
            stable_ratio=Decimal("0.3"),
        ),
    )

    borrowed = engine.borrow_to_target_hf(
        portfolio,
        Decimal("20"),
    )

    assert portfolio.wallet_usdc == Decimal("15") + borrowed


def test_open_clmm_position():
    portfolio = create_portfolio()

    portfolio.clmm = None
    portfolio.wallet_hype = Decimal("5")
    portfolio.wallet_usdc = Decimal("100")

    engine = RebalanceEngine(
        target_hf=Decimal("1.8"),
        strategy=HybridCGSStrategy(
            stable_ratio=Decimal("0.3"),
        ),
    )

    engine.open_clmm_position(
        portfolio=portfolio,
        hype_amount=Decimal("5"),
        usdc_amount=Decimal("100"),
        current_price=Decimal("20"),
        lower_price=Decimal("18"),
        upper_price=Decimal("22"),
    )

    assert portfolio.clmm is not None
    assert portfolio.wallet_hype == Decimal("0")
    assert portfolio.wallet_usdc == Decimal("0")


def test_open_clmm_position_negative_hype():
    portfolio = create_portfolio()

    portfolio.clmm = None

    engine = RebalanceEngine(
        target_hf=Decimal("1.8"),
        strategy=HybridCGSStrategy(
            stable_ratio=Decimal("0.3"),
        ),
    )

    with pytest.raises(ValueError, match="HYPE amount cannot be negative."):
        engine.open_clmm_position(
            portfolio=portfolio,
            hype_amount=Decimal("-1"),
            usdc_amount=Decimal("10"),
            current_price=Decimal("20"),
            lower_price=Decimal("18"),
            upper_price=Decimal("22"),
        )


def test_open_clmm_position_negative_usdc():
    portfolio = create_portfolio()

    portfolio.clmm = None

    engine = RebalanceEngine(
        target_hf=Decimal("1.8"),
        strategy=HybridCGSStrategy(
            stable_ratio=Decimal("0.3"),
        ),
    )

    with pytest.raises(ValueError, match="USDC amount cannot be negative."):
        engine.open_clmm_position(
            portfolio=portfolio,
            hype_amount=Decimal("1"),
            usdc_amount=Decimal("-10"),
            current_price=Decimal("20"),
            lower_price=Decimal("18"),
            upper_price=Decimal("22"),
        )


def test_open_clmm_position_not_enough_hype():
    portfolio = create_portfolio()

    portfolio.clmm = None
    portfolio.wallet_hype = Decimal("1")

    engine = RebalanceEngine(
        target_hf=Decimal("1.8"),
        strategy=HybridCGSStrategy(
            stable_ratio=Decimal("0.3"),
        ),
    )

    with pytest.raises(ValueError, match="Not enough HYPE in wallet."):
        engine.open_clmm_position(
            portfolio=portfolio,
            hype_amount=Decimal("5"),
            usdc_amount=Decimal("0"),
            current_price=Decimal("20"),
            lower_price=Decimal("18"),
            upper_price=Decimal("22"),
        )


def test_open_clmm_position_not_enough_usdc():
    portfolio = create_portfolio()

    portfolio.clmm = None
    portfolio.wallet_hype = Decimal("5")
    portfolio.wallet_usdc = Decimal("50")

    engine = RebalanceEngine(
        target_hf=Decimal("1.8"),
        strategy=HybridCGSStrategy(
            stable_ratio=Decimal("0.3"),
        ),
    )

    with pytest.raises(ValueError, match="Not enough USDC in wallet."):
        engine.open_clmm_position(
            portfolio=portfolio,
            hype_amount=Decimal("5"),
            usdc_amount=Decimal("100"),
            current_price=Decimal("20"),
            lower_price=Decimal("18"),
            upper_price=Decimal("22"),
        )


def test_open_clmm_position_does_not_modify_lending():
    portfolio = create_portfolio()

    portfolio.clmm = None
    portfolio.wallet_hype = Decimal("5")
    portfolio.wallet_usdc = Decimal("100")

    collateral_before = portfolio.lending.collateral_hype
    debt_before = portfolio.lending.debt_usdc

    engine = RebalanceEngine(
        target_hf=Decimal("1.8"),
        strategy=HybridCGSStrategy(
            stable_ratio=Decimal("0.3"),
        ),
    )

    engine.open_clmm_position(
        portfolio=portfolio,
        hype_amount=Decimal("5"),
        usdc_amount=Decimal("100"),
        current_price=Decimal("20"),
        lower_price=Decimal("18"),
        upper_price=Decimal("22"),
    )

    assert portfolio.lending.collateral_hype == collateral_before
    assert portfolio.lending.debt_usdc == debt_before


def test_rebalance_not_needed():
    portfolio = create_portfolio()

    wallet_hype_before = portfolio.wallet_hype
    wallet_usdc_before = portfolio.wallet_usdc
    debt_before = portfolio.lending.debt_usdc

    engine = RebalanceEngine(
        target_hf=Decimal("1.8"),
        strategy=HybridCGSStrategy(
            stable_ratio=Decimal("0.3"),
        ),
    )

    engine.rebalance(
        portfolio,
        Decimal("20"),
    )

    assert portfolio.clmm is not None
    assert portfolio.wallet_hype == wallet_hype_before
    assert portfolio.wallet_usdc == wallet_usdc_before
    assert portfolio.lending.debt_usdc == debt_before


def test_rebalance_restores_target_hf():
    portfolio = create_portfolio()

    engine = RebalanceEngine(
        target_hf=Decimal("1.8"),
        strategy=HybridCGSStrategy(
            stable_ratio=Decimal("0.3"),
        ),
    )

    engine.rebalance(
        portfolio,
        Decimal("25"),
    )

    assert (
        portfolio.lending.health_factor(
            Decimal("25"),
        )
        == engine.target_hf
    )


def test_rebalance_wallet_balances_non_negative():
    portfolio = create_portfolio()

    engine = RebalanceEngine(
        target_hf=Decimal("1.8"),
        strategy=HybridCGSStrategy(
            stable_ratio=Decimal("0.3"),
        ),
    )

    engine.rebalance(
        portfolio,
        Decimal("25"),
    )

    assert portfolio.wallet_hype >= Decimal("0")
    assert portfolio.wallet_usdc >= Decimal("0")


def test_rebalance_full_cycle():
    portfolio = create_portfolio()

    engine = RebalanceEngine(
        target_hf=Decimal("1.8"),
        strategy=HybridCGSStrategy(
            stable_ratio=Decimal("0.3"),
        ),
    )

    engine.rebalance(
        portfolio,
        Decimal("25"),
    )

    assert portfolio.clmm is not None
    assert portfolio.clmm.in_range(Decimal("25"))

    assert portfolio.stable_usdc > Decimal("0")

    assert portfolio.wallet_hype == Decimal("0")
    assert portfolio.wallet_usdc == Decimal("0")

    assert (
        portfolio.lending.health_factor(
            Decimal("25"),
        )
        >= engine.target_hf
    )
