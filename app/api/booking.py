from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.booking import Booking, BookingStatus
from app.models.user import ROLE_CUSTOMER, ROLE_RECRUITER, User
from app.schemas.booking import BookingCreate, BookingOut, BookingUpdate

router = APIRouter(prefix="/bookings", tags=["bookings"])


def _status_value(value) -> str:
    if hasattr(value, "value"):
        return value.value
    return str(value).lower()


def _booking_to_out(booking: Booking) -> BookingOut:
    return BookingOut(
        id=booking.id,
        customer_id=booking.customer_id,
        recruiter_id=booking.recruiter_id,
        booking_date=booking.booking_date,
        preferred_time=booking.preferred_time,
        care_type=booking.care_type,
        message=booking.message,
        status=_status_value(booking.status),
        created_at=booking.created_at,
        updated_at=booking.updated_at,
        customer_name=booking.customer.full_name if booking.customer else None,
        customer_email=booking.customer.email if booking.customer else None,
        customer_phone=booking.customer.phone if booking.customer else None,
        customer_address=booking.customer.address if booking.customer else None,
        customer_city=booking.customer.city if booking.customer else None,
        customer_state=booking.customer.state if booking.customer else None,
        customer_age=booking.customer.age if booking.customer else None,
        customer_emergency_contact=booking.customer.emergency_contact if booking.customer else None,
        recruiter_name=booking.recruiter.full_name if booking.recruiter else None,
        recruiter_email=booking.recruiter.email if booking.recruiter else None,
        recruiter_phone=booking.recruiter.phone if booking.recruiter else None,
        recruiter_address=booking.recruiter.address if booking.recruiter else None,
        recruiter_city=booking.recruiter.city if booking.recruiter else None,
        recruiter_state=booking.recruiter.state if booking.recruiter else None,
        recruiter_age=booking.recruiter.age if booking.recruiter else None,
    )


@router.post("", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
def create_booking(
    payload: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != ROLE_CUSTOMER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only customers can create bookings",
        )

    recruiter = db.get(User, payload.recruiter_id)
    if not recruiter or recruiter.role != ROLE_RECRUITER:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recruiter not found",
        )

    booking = Booking(
        customer_id=current_user.id,
        recruiter_id=payload.recruiter_id,
        booking_date=payload.booking_date,
        preferred_time=payload.preferred_time,
        care_type=payload.care_type,
        message=payload.message,
        status=BookingStatus.PENDING.value,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return _booking_to_out(booking)


@router.get("", response_model=list[BookingOut])
def get_my_bookings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role == ROLE_CUSTOMER:
        bookings = (
            db.query(Booking)
            .filter(Booking.customer_id == current_user.id)
            .order_by(Booking.created_at.desc())
            .all()
        )
    elif current_user.role == ROLE_RECRUITER:
        bookings = (
            db.query(Booking)
            .filter(Booking.recruiter_id == current_user.id)
            .order_by(Booking.created_at.desc())
            .all()
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid user role",
        )
    return [_booking_to_out(b) for b in bookings]


@router.get("/{booking_id}", response_model=BookingOut)
def get_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    booking = db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    if booking.customer_id != current_user.id and booking.recruiter_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    return _booking_to_out(booking)


@router.patch("/{booking_id}/status", response_model=BookingOut)
def update_booking_status(
    booking_id: int,
    payload: BookingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    booking = db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    if booking.recruiter_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the assigned recruiter can update booking status",
        )

    if _status_value(booking.status) != BookingStatus.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending bookings can be accepted or rejected",
        )

    booking.status = BookingStatus(payload.status)
    booking.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(booking)
    return _booking_to_out(booking)


@router.post("/{booking_id}/complete", response_model=BookingOut)
def complete_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    booking = db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    if booking.customer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the customer can mark booking as completed",
        )

    if _status_value(booking.status) != BookingStatus.ACCEPTED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only accepted bookings can be completed",
        )

    booking.status = BookingStatus.COMPLETED
    booking.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(booking)
    return _booking_to_out(booking)