from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from core.clmm import CLMMPosition
from core.lending import LendingPosition


@dataclass(slots=True)
class Portfolio:
    """
    Complete Hybrid CGS portfolio.
    """

    lending: LendingPosition

    clmm: CLMMPosition | None = None

    stable_usdc: Decimal = Decimal("0")

    wallet_hype: Decimal = Decimal("0")
    wallet_usdc: Decimal = Decimal("0")

    def total_hype(
        self,
        current_price: Decimal,
    ) -> Decimal:
        total = self.wallet_hype + self.lending.collateral_hype

        if self.clmm is not None:
            hype, _ = self.clmm.amounts(current_price)
            total += hype

        return total

    def total_usdc(
        self,
        current_price: Decimal,
    ) -> Decimal:
        total = self.wallet_usdc + self.stable_usdc

        if self.clmm is not None:
            _, usdc = self.clmm.amounts(current_price)
            total += usdc

        return total

    def assets_value(
        self,
        current_price: Decimal,
    ) -> Decimal:
        return self.total_hype(current_price) * current_price + self.total_usdc(current_price)

    def equity(
        self,
        current_price: Decimal,
    ) -> Decimal:
        return self.assets_value(current_price) - self.lending.debt_usdc

    def leverage(
        self,
        current_price: Decimal,
    ) -> Decimal:
        assets = self.assets_value(current_price)
        equity = self.equity(current_price)

        if assets == Decimal("0"):
            return Decimal("0")

        if equity <= Decimal("0"):
            return Decimal("Infinity")

        return assets / equity
