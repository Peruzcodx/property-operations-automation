from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class RentCreate(BaseModel):
    unit_id: int
    tenant_id: int
    rent_amount: Decimal
    due_date: date
    amount_paid: Decimal = Decimal("0")
    payment_date: date | None = None
    notes: str | None = None


class RentUpdate(BaseModel):
    amount_paid: Decimal | None = None
    payment_date: date | None = None
    payment_status: str | None = None
    notes: str | None = None


class RentResponse(BaseModel):
    id: int
    unit_id: int
    tenant_id: int
    rent_amount: Decimal
    due_date: date
    amount_paid: Decimal
    payment_date: date | None
    payment_status: str
    notes: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)