from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from core.income import accrue_stable_interest
from core.fees import accrue_clmm_fees
from core.portfolio import Portfolio
from core.rebalance import RebalanceEngine


@dataclass(slots=True)
class SimulationEngine:
    rebalance_engine: RebalanceEngine

    def step(
        self,
        portfolio: Portfolio,
        current_price: Decimal,
        days: int = 1,
    ) -> None:
        if days < 0:
            raise ValueError("days cannot be negative.")

        portfolio.lending.accrue_interest(days)

        accrue_stable_interest(
            portfolio,
            days,
        )

        if portfolio.clmm is not None:
            accrue_clmm_fees(
                portfolio.clmm,
                days,
            )

        self.rebalance_engine.rebalance(
            portfolio,
            current_price,
        )
