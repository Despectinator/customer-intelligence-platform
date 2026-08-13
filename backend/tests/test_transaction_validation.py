from datetime import date, timedelta
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas.transaction import TransactionCreate, TransactionUpdate


@pytest.mark.parametrize("amount", [Decimal("0"), Decimal("-1.00")])
def test_transaction_amount_must_be_positive(amount):
    with pytest.raises(ValidationError):
        TransactionCreate(order_date=date.today(), order_amount=amount)


def test_transaction_date_cannot_be_in_the_future():
    with pytest.raises(ValidationError):
        TransactionCreate(
            order_date=date.today() + timedelta(days=1),
            order_amount=Decimal("10.00"),
        )


def test_transaction_update_applies_the_same_date_validation():
    with pytest.raises(ValidationError):
        TransactionUpdate(order_date=date.today() + timedelta(days=1))


@pytest.mark.parametrize(
    ("value", "expected"),
    [("cash", "Cash"), ("CARD", "Card"), ("Bank Transfer", "Bank Transfer"), ("online", "Online"), ("Other", "Other")],
)
def test_payment_method_is_normalized_to_allowed_value(value, expected):
    transaction = TransactionCreate(
        order_date=date.today(), order_amount=Decimal("10.00"), payment_method=value
    )
    assert transaction.payment_method == expected


def test_payment_method_rejects_unknown_value():
    with pytest.raises(ValidationError):
        TransactionCreate(
            order_date=date.today(),
            order_amount=Decimal("10.00"),
            payment_method="Crypto Wallet",
        )
