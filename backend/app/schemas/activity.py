import uuid
from datetime import date

from pydantic import BaseModel


class ActivityOut(BaseModel):
    id: uuid.UUID
    label: str
    date: date
    status: str
