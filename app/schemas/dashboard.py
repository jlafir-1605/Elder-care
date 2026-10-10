from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.schemas.booking import RecruiterChargesOut


class DashboardProfile(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: int
    created_at: datetime
    phone: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    age: int | None = None
    emergency_contact: str | None = None
    charges: RecruiterChargesOut | None = None

    model_config = {"from_attributes": True}


class DashboardResponse(BaseModel):
    user: DashboardProfile
    contacts: list[DashboardProfile]