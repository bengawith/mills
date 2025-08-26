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
async def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user(db=db, user=user)

@router.post("/token", response_model=Token, tags=["Authentication"])
async def login_for_access_token(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Provides an access token for a valid user.
    This is the main login endpoint.
    """
    user = get_user(db, email=login_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    refresh_token_expires = timedelta(minutes=config.REFRESH_TOKEN_EXPIRE_MINUTES) # Assuming a refresh token expiry
    refresh_token = create_refresh_token(
        data={"sub": user.email}, expires_delta=refresh_token_expires
    )
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get("/users/me/", response_model=UserResponse, tags=["Authentication"])
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Fetches the profile of the currently authenticated user.
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