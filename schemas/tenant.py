from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TenantCreate(BaseModel):
    unit_id: int
    name: str
    email: str
    phone: str


class TenantResponse(BaseModel):
    id: int
    unit_id: int
    name: str
    email: str
    phone: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)