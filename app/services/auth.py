from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import Token, UserLogin, UserOut, UserRegister


class DuplicateEmailError(Exception):
    pass


def register_user(db: Session, payload: UserRegister) -> Token:
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing is not None:
        raise DuplicateEmailError()

    user = User(
        email=str(payload.email).lower(),
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _token_for(user)


def login_user(db: Session, payload: UserLogin) -> Token:
    user = db.query(User).filter(User.email == str(payload.email).lower()).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    return _token_for(user)


def _token_for(user: User) -> Token:
    return Token(
        access_token=create_access_token(user.id, user.role),
        token_type="bearer",
        user=UserOut.model_validate(user),
    )
