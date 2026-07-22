from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from core.clmm import CLMMPosition
from core.portfolio import Portfolio
from core.strategy import AllocationStrategy


@dataclass(slots=True)
class RebalanceEngine:
    target_hf: Decimal
    strategy: AllocationStrategy

    def needs_rebalance(
        self,
        portfolio: Portfolio,
        current_price: Decimal,
    ) -> bool:
        if portfolio.clmm is None:
            return False

        return not portfolio.clmm.in_range(current_price)

    def close_position(
        self,
        portfolio: Portfolio,
        current_price: Decimal,
    ) -> None:
        if portfolio.clmm is None:
            return

        hype, usdc = portfolio.clmm.amounts(current_price)

        portfolio.wallet_hype += hype
        portfolio.wallet_usdc += usdc

        portfolio.clmm = None

    def repay_debt(
        self,
        portfolio: Portfolio,
        amount: Decimal,
    ) -> Decimal:
        if amount < Decimal("0"):
            raise ValueError("Repayment amount cannot be negative.")

        repayment = min(
            amount,
            portfolio.wallet_usdc,
            portfolio.lending.debt_usdc,
        )

        portfolio.wallet_usdc -= repayment
        portfolio.lending.debt_usdc -= repayment

        return repayment

    def borrow_to_target_hf(
        self,
        portfolio: Portfolio,
        current_price: Decimal,
    ) -> Decimal:
        collateral_value = portfolio.lending.collateral_value(current_price)

        target_debt = collateral_value * portfolio.lending.liquidation_threshold / self.target_hf

        if portfolio.lending.debt_usdc >= target_debt:
            return Decimal("0")

        borrow_amount = target_debt - portfolio.lending.debt_usdc

        portfolio.lending.borrow(borrow_amount)
        portfolio.wallet_usdc += borrow_amount

        return borrow_amount

    def open_clmm_position(
        self,
        portfolio: Portfolio,
        hype_amount: Decimal,
        usdc_amount: Decimal,
        current_price: Decimal,
        lower_price: Decimal,
        upper_price: Decimal,
    ) -> None:
        if hype_amount < Decimal("0"):
            raise ValueError("HYPE amount cannot be negative.")

        if usdc_amount < Decimal("0"):
            raise ValueError("USDC amount cannot be negative.")

        if hype_amount > portfolio.wallet_hype:
            raise ValueError("Not enough HYPE in wallet.")

        if usdc_amount > portfolio.wallet_usdc:
            raise ValueError("Not enough USDC in wallet.")

        portfolio.clmm = CLMMPosition.from_amounts(
            amount0=hype_amount,
            amount1=usdc_amount,
            current_price=current_price,
            lower_price=lower_price,
            upper_price=upper_price,
        )

        portfolio.wallet_hype -= hype_amount
        portfolio.wallet_usdc -= usdc_amount

    def rebalance(
        self,
        portfolio: Portfolio,
        current_price: Decimal,
    ) -> None:
        if not self.needs_rebalance(
            portfolio,
            current_price,
        ):
            return

        self.close_position(
            portfolio,
            current_price,
        )

        self.repay_debt(
            portfolio,
            portfolio.wallet_usdc,
        )

        self.borrow_to_target_hf(
            portfolio,
            current_price,
        )

        allocation = self.strategy.allocate(
            portfolio,
            current_price,
        )

        portfolio.stable_usdc = allocation.stable_usdc
        portfolio.wallet_usdc -= allocation.stable_usdc

        lower = current_price * Decimal("0.9")
        upper = current_price * Decimal("1.1")

        self.open_clmm_position(
            portfolio,
            hype_amount=allocation.clmm_hype,
            usdc_amount=allocation.clmm_usdc,
            current_price=current_price,
            lower_price=lower,
            upper_price=upper,
        )
