from datetime import datetime, timedelta
from typing import Any, Dict, Optional, cast

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from aiconsole.api.auth.config import get_auth_settings
from aiconsole.api.auth.models.token import TokenData
from aiconsole.api.auth.models.user import User

# Use HTTPBearer instead of OAuth2PasswordBearer for simpler token authentication
security = HTTPBearer(auto_error=False)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: The data to encode in the token
        expires_delta: Optional expiration time, defaults to settings value

    Returns:
        The encoded JWT token as a string
    """
    auth_settings = get_auth_settings()
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=auth_settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, auth_settings.JWT_SECRET_KEY, algorithm=auth_settings.JWT_ALGORITHM)

    return encoded_jwt


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """
    Validate the access token and return the current user.

    Args:
        credentials: The HTTP Authorization header credentials

    Returns:
        The current user

    Raises:
        HTTPException: If the token is invalid or expired
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    auth_settings = get_auth_settings()

    try:
        payload = jwt.decode(token, auth_settings.JWT_SECRET_KEY, algorithms=[auth_settings.JWT_ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Cast to ensure user_id is str
        user_id_str = cast(str, user_id)
        token_data = TokenData(user_id=user_id_str)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # In a real application, you would fetch the user from a database
    # For this implementation, we'll create a user from the token data
    user = User(
        id=token_data.user_id,
        email=payload.get("email"),
        name=payload.get("name"),
        avatar_url=payload.get("avatar_url"),
        provider=payload.get("provider", "github"),
    )

    return user
