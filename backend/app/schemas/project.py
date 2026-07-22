import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    description: Optional[str] = None
    created_at: datetime
