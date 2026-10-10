from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.booking import Booking, BookingStatus, Review
from app.models.user import ROLE_CUSTOMER, User
from app.schemas.booking import ReviewCreate, ReviewOut

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
def create_review(
    payload: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != ROLE_CUSTOMER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only customers can create reviews",
        )

    booking = db.get(Booking, payload.booking_id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    if booking.customer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only review your own bookings",
        )

    if booking.status != BookingStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only review completed bookings",
        )

    existing = db.query(Review).filter(Review.booking_id == payload.booking_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Review already exists for this booking",
        )

    review = Review(
        customer_id=current_user.id,
        recruiter_id=booking.recruiter_id,
        booking_id=payload.booking_id,
        rating=payload.rating,
        review_text=payload.review_text,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return ReviewOut(
        id=review.id,
        customer_id=review.customer_id,
        recruiter_id=review.recruiter_id,
        booking_id=review.booking_id,
        rating=review.rating,
        review_text=review.review_text,
        created_at=review.created_at,
        customer_name=current_user.full_name,
    )


@router.get("/recruiter/{recruiter_id}", response_model=list[ReviewOut])
def get_recruiter_reviews(
    recruiter_id: int,
    db: Session = Depends(get_db),
):
    reviews = (
        db.query(Review)
        .filter(Review.recruiter_id == recruiter_id)
        .order_by(Review.created_at.desc())
        .all()
    )
    return [
        ReviewOut(
            id=r.id,
            customer_id=r.customer_id,
            recruiter_id=r.recruiter_id,
            booking_id=r.booking_id,
            rating=r.rating,
            review_text=r.review_text,
            created_at=r.created_at,
            customer_name=r.customer.full_name if r.customer else None,
        )
        for r in reviews
    ]


@router.get("/recruiter/{recruiter_id}/summary")
def get_recruiter_review_summary(
    recruiter_id: int,
    db: Session = Depends(get_db),
):
    reviews = db.query(Review).filter(Review.recruiter_id == recruiter_id).all()
    if not reviews:
        return {"average_rating": 0, "total_reviews": 0, "reviews": []}

    total = len(reviews)
    avg = sum(r.rating for r in reviews) / total

    recent = (
        db.query(Review)
        .filter(Review.recruiter_id == recruiter_id)
        .order_by(Review.created_at.desc())
        .limit(5)
        .all()
    )

    return {
        "average_rating": round(avg, 1),
        "total_reviews": total,
        "reviews": [
            ReviewOut(
                id=r.id,
                customer_id=r.customer_id,
                recruiter_id=r.recruiter_id,
                booking_id=r.booking_id,
                rating=r.rating,
                review_text=r.review_text,
                created_at=r.created_at,
                customer_name=r.customer.full_name if r.customer else None,
            )
            for r in recent
        ],
    }


@router.get("/booking/{booking_id}/can-review", response_model=bool)
def can_review_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    booking = db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    if booking.customer_id != current_user.id:
        return False

    if booking.status != BookingStatus.COMPLETED:
        return False

    existing = db.query(Review).filter(Review.booking_id == booking_id).first()
    return existing is None