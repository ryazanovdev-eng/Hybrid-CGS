from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from core.uniswap_math import amounts_from_liquidity, liquidity_from_amounts


@dataclass(slots=True)
class CLMMPosition:
    """
    Concentrated Liquidity Market Maker position.
    """

    liquidity: Decimal
    lower_price: Decimal
    upper_price: Decimal

    fee_token0: Decimal = Decimal("0")
    fee_token1: Decimal = Decimal("0")

    @classmethod
    def from_amounts(
        cls,
        amount0: Decimal,
        amount1: Decimal,
        current_price: Decimal,
        lower_price: Decimal,
        upper_price: Decimal,
    ) -> CLMMPosition:
        """
        Create a CLMM position from token amounts.
        """

        liquidity = liquidity_from_amounts(
            amount0,
            amount1,
            current_price.sqrt(),
            lower_price.sqrt(),
            upper_price.sqrt(),
        )

        return cls(
            liquidity=liquidity,
            lower_price=lower_price,
            upper_price=upper_price,
        )

    @property
    def sqrt_lower(self) -> Decimal:
        return self.lower_price.sqrt()

    @property
    def sqrt_upper(self) -> Decimal:
        return self.upper_price.sqrt()

    def amounts(
        self,
        current_price: Decimal,
    ) -> tuple[Decimal, Decimal]:
        """
        Return token amounts at the current market price.
        """

        return amounts_from_liquidity(
            self.liquidity,
            current_price.sqrt(),
            self.sqrt_lower,
            self.sqrt_upper,
        )

    def in_range(
        self,
        current_price: Decimal,
    ) -> bool:
        return self.lower_price <= current_price <= self.upper_price

    def value(
        self,
        current_price: Decimal,
    ) -> Decimal:
        amount0, amount1 = self.amounts(current_price)

        return amount0 * current_price + amount1
