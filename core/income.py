from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from core.portfolio import Portfolio


@dataclass(slots=True)
class IncomeEngine:
    """
    Daily income calculations for Hybrid CGS.
    """

    stable_apr: Decimal

    def accrue_stable_interest(
        self,
        portfolio: Portfolio,
        days: Decimal = Decimal("1"),
    ) -> Decimal:
        """
        Accrue interest on stable balance.

        Returns
        -------
        Decimal
            Earned USDC.
        """

        if days < 0:
            raise ValueError("Days cannot be negative.")

        daily_rate = self.stable_apr / Decimal("365")

        growth = (Decimal("1") + daily_rate) ** days

        before = portfolio.stable_usdc

        portfolio.stable_usdc *= growth

        return portfolio.stable_usdc - before
