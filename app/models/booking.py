from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class BookingStatus(str, PyEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class CareType(str, PyEnum):
    HOURLY = "hourly"
    DAILY = "daily"
    LIVE_IN = "live_in"
    MEDICAL = "medical"
    COMPANIONSHIP = "companionship"
    PERSONAL_CARE = "personal_care"
    OTHER = "other"


class VerificationStatus(str, PyEnum):
    NOT_VERIFIED = "not_verified"
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    recruiter_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    booking_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    preferred_time: Mapped[str] = mapped_column(String(50), nullable=False)
    care_type: Mapped[str] = mapped_column(String(50), nullable=False)
    message: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20),
        default=BookingStatus.PENDING.value,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    customer: Mapped["User"] = relationship("User", foreign_keys=[customer_id], back_populates="bookings_as_customer")
    recruiter: Mapped["User"] = relationship("User", foreign_keys=[recruiter_id], back_populates="bookings_as_recruiter")
    review: Mapped["Review"] = relationship("Review", back_populates="booking", uselist=False)


class RecruiterCharges(Base):
    __tablename__ = "recruiter_charges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    recruiter_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    hourly_charge: Mapped[float | None] = mapped_column(nullable=True)
    daily_charge: Mapped[float | None] = mapped_column(nullable=True)
    service_charges: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    recruiter: Mapped["User"] = relationship("User", back_populates="charges")


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    recruiter_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    booking_id: Mapped[int] = mapped_column(Integer, ForeignKey("bookings.id"), unique=True, nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    review_text: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    customer: Mapped["User"] = relationship("User", foreign_keys=[customer_id], back_populates="reviews_as_customer")
    recruiter: Mapped["User"] = relationship("User", foreign_keys=[recruiter_id], back_populates="reviews_as_recruiter")
    booking: Mapped["Booking"] = relationship("Booking", back_populates="review")


class RecruiterVerification(Base):
    __tablename__ = "recruiter_verifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    recruiter_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    document_type: Mapped[str] = mapped_column(String(100), nullable=False)
    document_reference: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(Enum(VerificationStatus), default=VerificationStatus.NOT_VERIFIED, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_by: Mapped[int | None] = mapped_column(Integer, nullable=True)
    admin_notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    recruiter: Mapped["User"] = relationship("User", back_populates="verification")