from decimal import Decimal

import pytest

from core.fees import FixedAPRFeeModel


def test_daily_fee_one_day():
    model = FixedAPRFeeModel(
        fee_apr=Decimal("0.40"),
    )

    earned = model.daily_fee(
        Decimal("1000"),
    )

    assert earned > Decimal("0")


def test_daily_fee_one_year():
    model = FixedAPRFeeModel(
        fee_apr=Decimal("0.40"),
    )

    earned = model.daily_fee(
        Decimal("1000"),
        Decimal("365"),
    )

    assert earned > Decimal("400")


def test_daily_fee_zero_days():
    model = FixedAPRFeeModel(
        fee_apr=Decimal("0.40"),
    )

    earned = model.daily_fee(
        Decimal("1000"),
        Decimal("0"),
    )

    assert earned == Decimal("0")


def test_daily_fee_negative_days():
    model = FixedAPRFeeModel(
        fee_apr=Decimal("0.40"),
    )

    with pytest.raises(ValueError):
        model.daily_fee(
            Decimal("1000"),
            Decimal("-1"),
        )
