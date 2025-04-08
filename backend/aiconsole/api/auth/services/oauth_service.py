import secrets
from typing import Any, Dict
from urllib.parse import urlencode

import httpx
from fastapi import HTTPException, status

from aiconsole.api.auth.config import get_auth_settings
from aiconsole.api.auth.models.user import User


def get_authorization_url(redirect_uri: str) -> Dict[str, str]:
    """
    Generate GitHub OAuth authorization URL with state parameter.

    This function creates a manual OAuth flow without using Authlib.

    Args:
        redirect_uri: The callback URL for GitHub OAuth

    Returns:
        Dictionary with auth_url and state
    """
    auth_settings = get_auth_settings()

    # Verify required settings
    if not auth_settings.GITHUB_CLIENT_ID or not auth_settings.GITHUB_CLIENT_SECRET:
        raise ValueError(
            "GitHub OAuth settings are missing. Please set GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET in .env file."
        )

    # Generate secure state parameter
    state = secrets.token_urlsafe(32)

    # Create authorization URL
    params = {
        "client_id": auth_settings.GITHUB_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "scope": "user:email read:user",
        "state": state,
    }

    auth_url = f"https://github.com/login/oauth/authorize?{urlencode(params)}"

    return {"auth_url": auth_url, "state": state}


async def get_access_token(code: str, state: str, expected_state: str) -> Dict[str, Any]:
    """
    Exchange authorization code for access token.

    Args:
        code: The authorization code from GitHub
        state: The state parameter returned from GitHub
        expected_state: The state we generated initially

    Returns:
        Dictionary with access_token and other token information

    Raises:
        HTTPException: If state validation fails or token retrieval fails
    """
    # Verify state to prevent CSRF attacks
    if state != expected_state:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid state parameter")

    auth_settings = get_auth_settings()

    # Exchange code for access token
    token_url = "https://github.com/login/oauth/access_token"

    # Prepare request data
    data = {
        "client_id": auth_settings.GITHUB_CLIENT_ID,
        "client_secret": auth_settings.GITHUB_CLIENT_SECRET,
        "code": code,
        "redirect_uri": auth_settings.GITHUB_CALLBACK_URL,
    }

    headers = {"Accept": "application/json"}

    # Make request to GitHub
    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=data, headers=headers)

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to retrieve access token: {response.text}"
        )

    # Parse token response
    token_data = response.json()

    if "access_token" not in token_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"No access token in response: {token_data}"
        )

    return token_data


async def get_github_user(token: str) -> User:
    """
    Retrieve user information from GitHub using the OAuth token.

    Args:
        token: The OAuth access token

    Returns:
        User object with GitHub profile information

    Raises:
        HTTPException: If the GitHub API request fails
    """
    # Get user info from GitHub API
    user_url = "https://api.github.com/user"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}

    async with httpx.AsyncClient() as client:
        response = await client.get(user_url, headers=headers)

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Failed to get user information from GitHub: {response.text}",
        )

    user_data = response.json()

    # Get user email if not public
    if not user_data.get("email"):
        emails_url = "https://api.github.com/user/emails"

        async with httpx.AsyncClient() as client:
            emails_response = await client.get(emails_url, headers=headers)

        if emails_response.status_code == 200:
            emails = emails_response.json()
            primary_email = next((email for email in emails if email.get("primary")), None)
            if primary_email:
                user_data["email"] = primary_email.get("email")

    # Create user object
    return User(
        id=str(user_data["id"]),
        email=user_data.get("email"),
        name=user_data.get("name") or user_data.get("login"),
        avatar_url=user_data.get("avatar_url"),
        provider="github",
    )
