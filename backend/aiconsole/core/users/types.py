
from pydantic import Base64Bytes, BaseModel, model_validator, BaseModel, EmailStr, HttpUrl, model_validator
from typing import Optional


DEFAULT_USERNAME = "user"


class PartialUserProfile(BaseModel):
    display_name: str | None = None
    profile_picture: Base64Bytes | None = None


class UserProfile(BaseModel):
    display_name: str
    profile_picture: Base64Bytes
