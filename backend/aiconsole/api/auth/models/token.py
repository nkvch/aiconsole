from pydantic import BaseModel


class Token(BaseModel):
    """Token model for authentication."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token data model containing user ID."""

    user_id: str
