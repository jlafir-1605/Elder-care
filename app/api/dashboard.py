from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.booking import RecruiterCharges
from app.models.user import ROLE_CUSTOMER, ROLE_RECRUITER, User
from app.schemas.booking import RecruiterChargesOut
from app.schemas.dashboard import DashboardProfile, DashboardResponse

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _profile(user: User, charges: RecruiterChargesOut | None = None) -> DashboardProfile:
    return DashboardProfile.model_validate(
        {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
            "created_at": user.created_at,
            "phone": user.phone,
            "address": user.address,
            "city": user.city,
            "state": user.state,
            "age": user.age,
            "emergency_contact": user.emergency_contact,
            "charges": charges,
        }
    )


@router.get("", response_model=DashboardResponse)
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    contact_role = ROLE_CUSTOMER if current_user.role == ROLE_RECRUITER else ROLE_RECRUITER
    contacts = (
        db.query(User)
        .filter(User.role == contact_role)
        .order_by(User.full_name.asc())
        .all()
    )
    profile_ids = [current_user.id, *(user.id for user in contacts)]
    charges_by_recruiter_id = {
        charges.recruiter_id: RecruiterChargesOut.model_validate(charges)
        for charges in db.query(RecruiterCharges)
        .filter(RecruiterCharges.recruiter_id.in_(profile_ids))
        .all()
    }
    return DashboardResponse(
        user=_profile(current_user, charges_by_recruiter_id.get(current_user.id)),
        contacts=[
            _profile(user, charges_by_recruiter_id.get(user.id))
            for user in contacts
        ],
    )