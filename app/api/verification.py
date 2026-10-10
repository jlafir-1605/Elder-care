from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.booking import RecruiterVerification, VerificationStatus
from app.models.user import ROLE_RECRUITER, User
from app.schemas.booking import RecruiterVerificationCreate, RecruiterVerificationOut, VerificationStatusOut

router = APIRouter(prefix="/verification", tags=["verification"])


@router.post("", response_model=RecruiterVerificationOut, status_code=status.HTTP_201_CREATED)
def submit_verification(
    payload: RecruiterVerificationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != ROLE_RECRUITER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can submit verification",
        )

    existing = db.query(RecruiterVerification).filter(RecruiterVerification.recruiter_id == current_user.id).first()
    if existing:
        if existing.status == VerificationStatus.VERIFIED:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Already verified",
            )
        if existing.status == VerificationStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Verification already pending",
            )
        existing.document_type = payload.document_type
        existing.document_reference = payload.document_reference
        existing.status = VerificationStatus.PENDING
        existing.submitted_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(existing)
        return RecruiterVerificationOut.model_validate(existing)

    verification = RecruiterVerification(
        recruiter_id=current_user.id,
        document_type=payload.document_type,
        document_reference=payload.document_reference,
        status=VerificationStatus.PENDING,
    )
    db.add(verification)
    db.commit()
    db.refresh(verification)
    return RecruiterVerificationOut.model_validate(verification)


@router.get("", response_model=RecruiterVerificationOut)
def get_my_verification(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != ROLE_RECRUITER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can access verification",
        )

    verification = db.query(RecruiterVerification).filter(RecruiterVerification.recruiter_id == current_user.id).first()
    if not verification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No verification submitted")
    return RecruiterVerificationOut.model_validate(verification)


@router.get("/recruiter/{recruiter_id}", response_model=VerificationStatusOut)
def get_recruiter_verification_status(
    recruiter_id: int,
    db: Session = Depends(get_db),
):
    verification = db.query(RecruiterVerification).filter(RecruiterVerification.recruiter_id == recruiter_id).first()
    if not verification:
        return VerificationStatusOut(status=VerificationStatus.NOT_VERIFIED)

    return VerificationStatusOut(
        status=verification.status.value if hasattr(verification.status, 'value') else verification.status,
        document_type=verification.document_type if verification.status == VerificationStatus.VERIFIED else None,
        submitted_at=verification.submitted_at,
        reviewed_at=verification.reviewed_at,
    )


# Admin endpoints for verification management
@router.put("/{verification_id}/approve", response_model=RecruiterVerificationOut)
def approve_verification(
    verification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Simple admin check - in production, use proper admin role
    verification = db.get(RecruiterVerification, verification_id)
    if not verification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Verification not found")

    verification.status = VerificationStatus.VERIFIED
    verification.reviewed_at = datetime.now(datetime.timezone.utc)
    verification.reviewed_by = current_user.id
    db.commit()
    db.refresh(verification)
    return RecruiterVerificationOut.model_validate(verification)


@router.put("/{verification_id}/reject", response_model=RecruiterVerificationOut)
def reject_verification(
    verification_id: int,
    admin_notes: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    verification = db.get(RecruiterVerification, verification_id)
    if not verification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Verification not found")

    verification.status = VerificationStatus.REJECTED
    verification.reviewed_at = datetime.now(datetime.timezone.utc)
    verification.reviewed_by = current_user.id
    verification.admin_notes = admin_notes
    db.commit()
    db.refresh(verification)
    return RecruiterVerificationOut.model_validate(verification)