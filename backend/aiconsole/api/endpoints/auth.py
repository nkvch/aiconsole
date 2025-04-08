from fastapi import APIRouter, Request, HTTPException
from starlette.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from aiconsole.core.settings.settings import settings
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
config = Config(".env")

oauth = OAuth(config)
oauth.register(
    name="github",
    client_id=settings().github_client_id,
    client_secret=settings().github_client_secret,
    access_token_url="https://github.com/login/oauth/access_token",
    authorize_url="https://github.com/login/oauth/authorize",
    api_base_url="https://api.github.com/",
    client_kwargs={"scope": "user:email"},
)


@router.get("/login/github")
async def login(request: Request):
    redirect_uri = request.url_for("auth_callback")
    return await oauth.github.authorize_redirect(request, redirect_uri)


@router.get("/github/callback")
async def auth_callback(request: Request):
    token = await oauth.github.authorize_access_token(request)
    user = await oauth.github.get("user", token=token)
    profile = user.json()

    email = profile.get("email")
    if not email:
        emails_resp = await oauth.github.get("user/emails", token=token)
        emails = emails_resp.json()
        email = next((e["email"] for e in emails if e["primary"]), None)

    if not email:
        raise HTTPException(status_code=400, detail="Email not found")

    response = RedirectResponse(url="http://localhost:3000/")
    response.set_cookie("user", email, httponly=True, samesite="Lax")
    logger.info(f"Set cookie 'user' with value: {email}")
    return response


@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie("user")
    return response


@router.get("/me")
async def me(request: Request):
    user = request.cookies.get("user")
    return {"email": user if user else None}
