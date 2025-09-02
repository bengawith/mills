from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordRequestForm # Removed OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import get_db
from database_models import User
from schemas import Token, UserCreate, UserResponse, UserUpdate, LoginRequest # Added LoginRequest
from security import create_access_token, create_refresh_token, verify_password, get_user, get_current_active_user, create_user
from const.config import config

router = APIRouter()

@router.post("/users/", response_model=UserResponse, tags=["Authentication"])
async def create_new_user(user: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    """
    Creates a new user in the database.
    Args:
        user (UserCreate): User creation data.
        db (Session): SQLAlchemy database session (injected).
    Returns:
        UserResponse: The created user response model.
    Raises:
        HTTPException: If email is already registered.
    """
    db_user = get_user(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user(db=db, user=user)

@router.post("/token", response_model=Token, tags=["Authentication"])
async def login_for_access_token(login_data: LoginRequest, db: Session = Depends(get_db)) -> dict:
    """
    Provides an access token and refresh token for a valid user.
    Args:
        login_data (LoginRequest): Login credentials (email, password).
        db (Session): SQLAlchemy database session (injected).
    Returns:
        dict: Dictionary containing access_token, refresh_token, and token_type.
    Raises:
        HTTPException: If credentials are invalid.
    """
    user = get_user(db, email=login_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Fix: Extract string value from SQLAlchemy column if necessary
    hashed_password = user.hashed_password if isinstance(user.hashed_password, str) else str(user.hashed_password)
    if not verify_password(login_data.password, hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    refresh_token_expires = timedelta(minutes=config.REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token = create_refresh_token(
        data={"sub": user.email}, expires_delta=refresh_token_expires
    )
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get("/users/me/", response_model=UserResponse, tags=["Authentication"])
async def read_users_me(current_user: User = Depends(get_current_active_user)) -> UserResponse:
    """
    Fetches the profile of the currently authenticated user.
    Args:
        current_user (User): The current authenticated user (injected).
    Returns:
        UserResponse: The current user's profile.
    """
    return current_user

@router.patch("/users/me/", response_model=UserResponse, tags=["Authentication"])
async def update_user_me(user_update: UserUpdate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(current_user, field, value)
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user
