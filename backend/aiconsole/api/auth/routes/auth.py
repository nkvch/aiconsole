from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse, RedirectResponse

from aiconsole.api.auth.config import get_auth_settings
from aiconsole.api.auth.models.user import User, UserResponse
from aiconsole.api.auth.services.oauth_service import (
    get_access_token,
    get_authorization_url,
    get_github_user,
)
from aiconsole.api.auth.services.token_service import (
    create_access_token,
    get_current_user,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# In a production app, I would use a proper storage like Redis
AUTH_STATES = {}


@router.get("/login")
async def login():
    """
    Redirect to GitHub OAuth login page.
    """
    try:
        auth_settings = get_auth_settings()
        # Get GitHub authorization URL
        auth_data = get_authorization_url(redirect_uri=auth_settings.GITHUB_CALLBACK_URL)

        # Store state for verification during callback
        state = auth_data["state"]
        AUTH_STATES[state] = {
            "created_at": auth_data.get("created_at", 0),
            "redirect_uri": auth_settings.GITHUB_CALLBACK_URL,
        }

        # Redirect to GitHub authorization page
        return RedirectResponse(url=auth_data["auth_url"])
    except ValueError as e:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": str(e)})
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": f"Failed to initialize OAuth: {str(e)}"},
        )


@router.get("/callback")
async def auth_callback(code: str, state: str):
    """
    Handle OAuth callback from GitHub.

    After successful authentication, creates JWT token and redirects to frontend.
    """
    try:
        # Verify state exists in our store
        if state not in AUTH_STATES:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "Invalid state parameter"})

        # Remove state after verification (we don't need to use it further)
        AUTH_STATES.pop(state)
        auth_settings = get_auth_settings()

        # Exchange code for access token
        token_data = await get_access_token(code, state, state)
        token = token_data["access_token"]

        # Get user info from GitHub
        user = await get_github_user(token)

        # Create JWT token
        token_data: Dict[str, Any] = {
            "sub": user.id,
            "email": user.email,
            "name": user.name,
            "avatar_url": user.avatar_url,
            "provider": user.provider,
        }

        access_token = create_access_token(data=token_data)

        # Redirect to frontend with token
        redirect_url = f"{auth_settings.FRONTEND_URL}?token={access_token}"
        return RedirectResponse(url=redirect_url)
    except ValueError as e:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": str(e)})
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": f"Error processing callback: {str(e)}"},
        )


@router.get("/me", response_model=UserResponse)
async def get_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information.

    This endpoint is protected and requires a valid JWT token.
    """
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    return UserResponse(
        id=current_user.id, email=current_user.email, name=current_user.name, avatar_url=current_user.avatar_url
    )
