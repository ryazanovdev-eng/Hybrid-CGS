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
