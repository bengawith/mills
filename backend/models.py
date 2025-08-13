from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    """Pydantic model for the authentication token response."""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Pydantic model for the data encoded within a JWT token."""
    username: Optional[str] = None

class User(BaseModel):
    """Pydantic model for a user."""
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    """Pydantic model for a user as stored in the database, including the hashed password."""
    hashed_password: str
