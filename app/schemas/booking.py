from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator


class BookingBase(BaseModel):
    recruiter_id: int
    booking_date: datetime
    preferred_time: str = Field(min_length=1, max_length=50)
    care_type: Literal["hourly", "daily", "live_in", "medical", "companionship", "personal_care", "other"]
    message: str | None = Field(default=None, max_length=1000)


class BookingCreate(BookingBase):
    pass


class BookingUpdate(BaseModel):
    status: Literal["accepted", "rejected"]


class BookingOut(BaseModel):
    id: int
    customer_id: int
    recruiter_id: int
    booking_date: datetime
    preferred_time: str
    care_type: str
    message: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime
    customer_name: str | None = None
    customer_email: str | None = None
    customer_phone: str | None = None
    customer_address: str | None = None
    customer_city: str | None = None
    customer_state: str | None = None
    customer_age: int | None = None
    customer_emergency_contact: str | None = None
    recruiter_name: str | None = None
    recruiter_email: str | None = None
    recruiter_phone: str | None = None
    recruiter_address: str | None = None
    recruiter_city: str | None = None
    recruiter_state: str | None = None
    recruiter_age: int | None = None

    model_config = {"from_attributes": True}


class RecruiterChargesBase(BaseModel):
    hourly_charge: float | None = Field(default=None, ge=0)
    daily_charge: float | None = Field(default=None, ge=0)
    service_charges: str | None = Field(default=None, max_length=1000)


class RecruiterChargesCreate(RecruiterChargesBase):
    pass


class RecruiterChargesUpdate(RecruiterChargesBase):
    pass


class RecruiterChargesOut(BaseModel):
    id: int | None = None
    recruiter_id: int
    hourly_charge: float | None = None
    daily_charge: float | None = None
    service_charges: str | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class ReviewBase(BaseModel):
    booking_id: int
    rating: int = Field(ge=1, le=5)
    review_text: str | None = Field(default=None, max_length=2000)


class ReviewCreate(ReviewBase):
    pass


class ReviewOut(BaseModel):
    id: int
    customer_id: int
    recruiter_id: int
    booking_id: int
    rating: int
    review_text: str | None = None
    created_at: datetime
    customer_name: str | None = None

    model_config = {"from_attributes": True}


class RecruiterVerificationBase(BaseModel):
    document_type: str = Field(min_length=1, max_length=100)
    document_reference: str = Field(min_length=1, max_length=255)


class RecruiterVerificationCreate(RecruiterVerificationBase):
    pass


class RecruiterVerificationOut(BaseModel):
    id: int
    recruiter_id: int
    document_type: str
    document_reference: str
    status: str
    submitted_at: datetime
    reviewed_at: datetime | None = None
    admin_notes: str | None = None

    model_config = {"from_attributes": True}


class VerificationStatusOut(BaseModel):
    status: str
    document_type: str | None = None
    submitted_at: datetime | None = None
    reviewed_at: datetime | None = None