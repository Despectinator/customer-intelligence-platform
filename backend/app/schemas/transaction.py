import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


ALLOWED_PAYMENT_METHODS = (
    "Cash",
    "Card",
    "Bank Transfer",
    "Online",
    "Other",
)


def _validate_order_date(value: date | None) -> date | None:
    if value is not None and value > date.today():
        raise ValueError("order_date cannot be in the future")
    return value


def _normalize_payment_method(value: str | None) -> str | None:
    if value is None or not value.strip():
        return None

    normalized = value.strip().casefold()
    for allowed in ALLOWED_PAYMENT_METHODS:
        if normalized == allowed.casefold():
            return allowed

    allowed_values = ", ".join(ALLOWED_PAYMENT_METHODS)
    raise ValueError(f"payment_method must be one of: {allowed_values}")


class TransactionCreate(BaseModel):
    order_date: date
    order_amount: Decimal = Field(..., gt=0)
    payment_method: Optional[str] = Field(default=None, max_length=50)

    _order_date_not_future = field_validator("order_date")(_validate_order_date)
    _payment_method_allowed = field_validator("payment_method", mode="before")(
        _normalize_payment_method
    )


class TransactionUpdate(BaseModel):
    order_date: Optional[date] = None
    order_amount: Optional[Decimal] = Field(default=None, gt=0)
    payment_method: Optional[str] = Field(default=None, max_length=50)

    _order_date_not_future = field_validator("order_date")(_validate_order_date)
    _payment_method_allowed = field_validator("payment_method", mode="before")(
        _normalize_payment_method
    )


class TransactionOut(BaseModel):
    id: uuid.UUID
    customer_id: uuid.UUID
    order_date: date
    order_amount: Decimal
    payment_method: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
