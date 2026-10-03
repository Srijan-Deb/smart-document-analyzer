from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Any

from app.database.database import get_db
from app.models.user import User as DBUser
from app.schemas.user import UserCreate, User
from app.schemas.token import Token
from app.core.config import settings
from app.core.security import verify_password, get_password_hash, create_access_token, get_current_user

router = APIRouter()

@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = db.query(DBUser).filter(DBUser.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            subject=user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
        "user": user,
    }

@router.get("/me", response_model=User)
def get_current_user_profile(
    current_user: DBUser = Depends(get_current_user)
) -> Any:
    """
    Get current logged-in user profile
    """
    return current_user

@router.post("/register", response_model=User)
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """
    Register a new user
    """
    user = db.query(DBUser).filter(DBUser.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system",
        )
    user_by_username = db.query(DBUser).filter(DBUser.username == user_in.username).first()
    if user_by_username:
        raise HTTPException(
            status_code=400,
            detail="The username already exists in the system",
        )
    
    db_user = DBUser(
        email=user_in.email,
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
