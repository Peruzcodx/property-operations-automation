from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MaintenanceCreate(BaseModel):
    unit_id: int
    inspection_id: int | None = None
    description: str
    reported_by: str
    priority: str
    assigned_contractor: str | None = None


class MaintenanceUpdate(BaseModel):
    priority: str | None = None
    assigned_contractor: str | None = None
    status: str | None = None
    resolution_notes: str | None = None


class MaintenanceResponse(BaseModel):
    id: int
    unit_id: int
    inspection_id: int | None
    description: str
    reported_by: str
    priority: str
    assigned_contractor: str | None
    status: str
    created_at: datetime
    resolved_at: datetime | None
    resolution_notes: str | None

    model_config = ConfigDict(from_attributes=True)