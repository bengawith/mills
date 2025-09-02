
# ---
# Security utilities for authentication, password hashing, and JWT management.
# Handles user creation, token generation, and authentication dependencies for FastAPI.
# ---

from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import get_db
from database_models import User
from schemas import TokenData, UserCreate
from const.config import config


# --- Password Hashing Setup ---
# Uses bcrypt for secure password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# --- OAuth2 Scheme ---
# Defines the OAuth2 token endpoint for FastAPI authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


# Verifies a plain password against a hashed one
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Returns True if the plain password matches the hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)


# Hashes a plain password using bcrypt
def get_password_hash(password: str) -> str:
    """
    Returns a bcrypt hash of the given password.
    """
    return pwd_context.hash(password)


# Creates a new JWT access token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Generates a JWT access token with an expiration time.
    Default expiry is 15 minutes if not specified.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Default to 15 minutes if no expiry is provided
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt


# Creates a new JWT refresh token
def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Generates a JWT refresh token with an expiration time.
    Default expiry is 7 days if not specified.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Default to 7 days if no expiry is provided
        expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt


# Retrieves a user from the database by email
def get_user(db: Session, email: str):
    """
    Returns the User object for the given email, or None if not found.
    """
    return db.query(User).filter(User.email == email).first()


# Creates a new user in the database
def create_user(db: Session, user: UserCreate):
    """
    Hashes the password and creates a new User record in the database.
    Returns the created User object.
    """
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        hashed_password=hashed_password,
        role=user.role,
        onboarded=False # New users are not onboarded by default
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# --- User Authentication Dependency ---
# Dependency for FastAPI endpoints to get the current authenticated user
async def get_current_active_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Decodes the JWT token to get the current user.
    Raises an exception if the token is invalid, expired, or the user is inactive.
    Used as a dependency in protected routes.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing email (sub) claim",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token_data = TokenData(email=email)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token signature or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Only call get_user if email is not None
    if token_data.email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing email (sub) claim",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = get_user(db, email=token_data.email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found in database",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Access the actual value of user.disabled, not the column object
    if getattr(user, "disabled", False):
        raise HTTPException(status_code=400, detail="Inactive user")
    return user
