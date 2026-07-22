from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(slots=True)
class FixedAPRFeeModel:
    """
    Fixed CLMM APR fee model.
    """

    fee_apr: Decimal

    def daily_fee(
        self,
        position_value: Decimal,
        days: Decimal = Decimal("1"),
    ) -> Decimal:
        """
        Calculate earned fees.
        """

        if days < 0:
            raise ValueError("Days cannot be negative.")

        daily_rate = self.fee_apr / Decimal("365")

        growth = (Decimal("1") + daily_rate) ** days

        return position_value * (growth - Decimal("1"))
