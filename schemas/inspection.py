from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class InspectionCreate(BaseModel):
    unit_id: int
    inspection_type: str
    inspection_date: date
    inspector: str
    condition_notes: str | None = None
    flagged_issue: str | None = None


class InspectionResponse(BaseModel):
    id: int
    unit_id: int
    inspection_type: str
    inspection_date: date
    inspector: str
    condition_notes: str | None
    flagged_issue: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)