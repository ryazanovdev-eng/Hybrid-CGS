from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from core.portfolio import Portfolio


@dataclass(slots=True)
class Allocation:
    clmm_hype: Decimal
    clmm_usdc: Decimal
    stable_usdc: Decimal


class AllocationStrategy:
    def allocate(
        self,
        portfolio: Portfolio,
        current_price: Decimal,
    ) -> Allocation:
        raise NotImplementedError


@dataclass(slots=True)
class HybridCGSStrategy(AllocationStrategy):
    stable_ratio: Decimal

    def allocate(
        self,
        portfolio: Portfolio,
        current_price: Decimal,
    ) -> Allocation:
        if not (Decimal("0") <= self.stable_ratio <= Decimal("1")):
            raise ValueError("stable_ratio must be between 0 and 1.")

        stable = portfolio.wallet_usdc * self.stable_ratio
        clmm_usdc = portfolio.wallet_usdc - stable

        return Allocation(
            clmm_hype=portfolio.wallet_hype,
            clmm_usdc=clmm_usdc,
            stable_usdc=stable,
        )
