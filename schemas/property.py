from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PropertyResponse(BaseModel):
    id: int
    property_name: str
    address: str
    property_type: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PropertyCreate(BaseModel):
    property_name: str
    address: str
    property_type: str