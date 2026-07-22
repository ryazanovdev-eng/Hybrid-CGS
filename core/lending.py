from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

DEFAULT_LIQUIDATION_THRESHOLD = Decimal("0.74")
DEFAULT_COLLATERAL_APR = Decimal("0.019")
DEFAULT_BORROW_APR = Decimal("0.045")


@dataclass(slots=True)
class LendingPosition:
    """
    Lending position backed by HYPE collateral.
    """

    collateral_hype: Decimal
    debt_usdc: Decimal

    liquidation_threshold: Decimal = DEFAULT_LIQUIDATION_THRESHOLD

    collateral_apr: Decimal = DEFAULT_COLLATERAL_APR
    borrow_apr: Decimal = DEFAULT_BORROW_APR

    def collateral_value(
        self,
        hype_price: Decimal,
    ) -> Decimal:
        return self.collateral_hype * hype_price

    def ltv(
        self,
        hype_price: Decimal,
    ) -> Decimal:
        collateral = self.collateral_value(hype_price)

        if collateral == Decimal("0"):
            return Decimal("0")

        return self.debt_usdc / collateral

    def health_factor(
        self,
        hype_price: Decimal,
    ) -> Decimal:
        if self.debt_usdc == Decimal("0"):
            return Decimal("Infinity")

        collateral = self.collateral_value(hype_price)

        return collateral * self.liquidation_threshold / self.debt_usdc

    def borrow_capacity(
        self,
        hype_price: Decimal,
    ) -> Decimal:
        collateral = self.collateral_value(hype_price)

        return collateral * self.liquidation_threshold

    def deposit_collateral(
        self,
        amount: Decimal,
    ) -> None:
        """
        Deposit additional HYPE collateral.
        """

        if amount < 0:
            raise ValueError("Collateral amount cannot be negative.")

        self.collateral_hype += amount

    def withdraw_collateral(
        self,
        amount: Decimal,
    ) -> None:
        """
        Withdraw HYPE collateral.
        """

        if amount < 0:
            raise ValueError("Collateral amount cannot be negative.")

        if amount > self.collateral_hype:
            raise ValueError("Insufficient collateral.")

        self.collateral_hype -= amount

    def borrow(
        self,
        amount: Decimal,
    ) -> None:
        """
        Borrow additional USDC.
        """

        if amount < 0:
            raise ValueError("Borrow amount cannot be negative.")

        self.debt_usdc += amount

    def repay(
        self,
        amount: Decimal,
    ) -> None:
        """
        Repay borrowed USDC.
        """

        if amount < 0:
            raise ValueError("Repay amount cannot be negative.")

        if amount > self.debt_usdc:
            raise ValueError("Repay amount exceeds debt.")

        self.debt_usdc -= amount

    def accrue_interest(
        self,
        days: Decimal = Decimal("1"),
    ) -> None:
        """
        Accrue lending and borrowing interest.

        Parameters
        ----------
        days : Decimal
            Number of days.
        """

        if days < 0:
            raise ValueError("Days cannot be negative.")

        daily_collateral_rate = self.collateral_apr / Decimal("365")

        daily_borrow_rate = self.borrow_apr / Decimal("365")

        collateral_growth = (Decimal("1") + daily_collateral_rate) ** days

        borrow_growth = (Decimal("1") + daily_borrow_rate) ** days

        self.collateral_hype *= collateral_growth
        self.debt_usdc *= borrow_growth
