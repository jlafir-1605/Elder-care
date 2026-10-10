from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.booking import RecruiterCharges
from app.models.user import ROLE_RECRUITER, User
from app.schemas.booking import RecruiterChargesCreate, RecruiterChargesOut, RecruiterChargesUpdate

router = APIRouter(prefix="/charges", tags=["charges"])


@router.get("", response_model=RecruiterChargesOut)
def get_my_charges(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != ROLE_RECRUITER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can access charges",
        )

    charges = db.query(RecruiterCharges).filter(RecruiterCharges.recruiter_id == current_user.id).first()
    if not charges:
        charges = RecruiterCharges(recruiter_id=current_user.id)
        db.add(charges)
        db.commit()
        db.refresh(charges)
    return RecruiterChargesOut.model_validate(charges)


@router.get("/recruiter/{recruiter_id}", response_model=RecruiterChargesOut)
def get_recruiter_charges(
    recruiter_id: int,
    db: Session = Depends(get_db),
):
    recruiter = db.get(User, recruiter_id)
    if recruiter is None or recruiter.role != ROLE_RECRUITER:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recruiter not found")

    charges = db.query(RecruiterCharges).filter(RecruiterCharges.recruiter_id == recruiter_id).first()
    if not charges:
        return RecruiterChargesOut(recruiter_id=recruiter_id)
    return RecruiterChargesOut.model_validate(charges)


@router.post("", response_model=RecruiterChargesOut, status_code=status.HTTP_201_CREATED)
def create_charges(
    payload: RecruiterChargesCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != ROLE_RECRUITER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can create charges",
        )

    existing = db.query(RecruiterCharges).filter(RecruiterCharges.recruiter_id == current_user.id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Charges already exist. Use PUT to update.",
        )

    charges = RecruiterCharges(
        recruiter_id=current_user.id,
        hourly_charge=payload.hourly_charge,
        daily_charge=payload.daily_charge,
        service_charges=payload.service_charges,
    )
    db.add(charges)
    db.commit()
    db.refresh(charges)
    return RecruiterChargesOut.model_validate(charges)


@router.put("", response_model=RecruiterChargesOut)
def update_charges(
    payload: RecruiterChargesUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != ROLE_RECRUITER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can update charges",
        )

    charges = db.query(RecruiterCharges).filter(RecruiterCharges.recruiter_id == current_user.id).first()
    if not charges:
        charges = RecruiterCharges(recruiter_id=current_user.id)
        db.add(charges)

    if "hourly_charge" in payload.model_fields_set:
        charges.hourly_charge = payload.hourly_charge
    if "daily_charge" in payload.model_fields_set:
        charges.daily_charge = payload.daily_charge
    if "service_charges" in payload.model_fields_set:
        charges.service_charges = payload.service_charges

    db.commit()
    db.refresh(charges)
    return RecruiterChargesOut.model_validate(charges)