import re
from typing import List, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from aiconsole.api.auth.models.user import User
from aiconsole.api.auth.services.token_service import get_current_user

security = HTTPBearer()


class AuthMiddleware:
    """Middleware for authentication protection on routes."""

    def __init__(self, public_paths: Optional[List[str]] = None, exclude_paths: Optional[List[str]] = None):
        """
        Initialize middleware with public and excluded paths.

        Args:
            public_paths: List of path regex patterns that are accessible without authentication
            exclude_paths: List of path regex patterns to exclude from auth checking completely
        """
        self.public_paths = public_paths or [
            r"^/docs$",
            r"^/redoc$",
            r"^/openapi.json$",
            r"^/auth/login$",
            r"^/auth/callback$",
            r"^/ping$",
        ]
        self.exclude_paths = exclude_paths or []

        # Precompile path patterns
        self.public_paths_regex = [re.compile(path) for path in self.public_paths]
        self.exclude_paths_regex = [re.compile(path) for path in self.exclude_paths]

    def is_path_public(self, path: str) -> bool:
        """Check if path is public."""
        return any(regex.match(path) for regex in self.public_paths_regex)

    def is_path_excluded(self, path: str) -> bool:
        """Check if path is excluded from auth checking."""
        return any(regex.match(path) for regex in self.exclude_paths_regex)

    async def __call__(
        self,
        request: Request,
        credentials: HTTPAuthorizationCredentials = Depends(security),
        user: User = Depends(get_current_user),
    ):
        """
        Authenticate request based on path and token.

        Args:
            request: The request to authenticate
            credentials: HTTP bearer credentials
            user: Current authenticated user

        Raises:
            HTTPException: If authentication fails
        """
        path = request.url.path

        # Skip excluded paths
        if self.is_path_excluded(path):
            return

        # Allow public paths
        if self.is_path_public(path):
            return

        # Check authentication
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
