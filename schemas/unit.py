from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UnitCreate(BaseModel):
    property_id: int
    unit_name: str


class UnitResponse(BaseModel):
    id: int
    property_id: int
    unit_name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)