from typing import Optional

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    """User model containing user information."""

    id: str
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    provider: str = "github"


class UserResponse(BaseModel):
    """User response model for API endpoints."""

    id: str
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    avatar_url: Optional[str] = None
