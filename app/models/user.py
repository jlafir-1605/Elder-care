from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

ROLE_RECRUITER = 1
ROLE_CUSTOMER = 2


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[int] = mapped_column(
        Integer, nullable=False, default=ROLE_CUSTOMER
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    emergency_contact: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )

    bookings_as_customer: Mapped[list["Booking"]] = relationship(
        "Booking",
        foreign_keys="Booking.customer_id",
        back_populates="customer",
    )
    bookings_as_recruiter: Mapped[list["Booking"]] = relationship(
        "Booking",
        foreign_keys="Booking.recruiter_id",
        back_populates="recruiter",
    )
    charges: Mapped["RecruiterCharges | None"] = relationship(
        "RecruiterCharges",
        back_populates="recruiter",
        uselist=False,
    )
    reviews_as_customer: Mapped[list["Review"]] = relationship(
        "Review",
        foreign_keys="Review.customer_id",
        back_populates="customer",
    )
    reviews_as_recruiter: Mapped[list["Review"]] = relationship(
        "Review",
        foreign_keys="Review.recruiter_id",
        back_populates="recruiter",
    )
    verification: Mapped["RecruiterVerification | None"] = relationship(
        "RecruiterVerification",
        back_populates="recruiter",
        uselist=False,
    )
