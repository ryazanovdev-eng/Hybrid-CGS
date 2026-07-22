from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from core.portfolio import Portfolio


@dataclass(slots=True)
class RebalanceEngine:
    target_hf: Decimal

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
