import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TransactionCreate(BaseModel):
    order_date: date
    order_amount: Decimal = Field(..., gt=0)
    payment_method: Optional[str] = Field(default=None, max_length=50)


class TransactionUpdate(BaseModel):
    order_date: Optional[date] = None
    order_amount: Optional[Decimal] = Field(default=None, gt=0)
    payment_method: Optional[str] = Field(default=None, max_length=50)


class TransactionOut(BaseModel):
    id: uuid.UUID
    customer_id: uuid.UUID
    order_date: date
    order_amount: Decimal
    payment_method: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)