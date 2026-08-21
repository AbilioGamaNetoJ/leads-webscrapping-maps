import os
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database.connection import get_db
from services.auth import is_safe_return_to, require_same_origin
from services.clerk import (
    ClerkApiError,
    ClerkConfigurationError,
    get_user_profile,
    verify_session_token,
)
from services.users import upsert_user

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))
DbSession = Annotated[Session, Depends(get_db)]
SameOrigin = Annotated[None, Depends(require_same_origin)]


@router.get("/login")
def login(request: Request, return_to: str = "/"):
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "return_to": is_safe_return_to(return_to),
            "clerk_publishable_key": os.getenv("CLERK_PUBLISHABLE_KEY", ""),
            "clerk_frontend_api_url": os.getenv("CLERK_FRONTEND_API_URL", ""),
        },
    )


@router.get("/auth/complete")
def complete_auth(request: Request, return_to: str = "/"):
    return templates.TemplateResponse(
        "auth_complete.html",
        {
            "request": request,
            "return_to": is_safe_return_to(return_to),
            "clerk_publishable_key": os.getenv("CLERK_PUBLISHABLE_KEY", ""),
            "clerk_frontend_api_url": os.getenv("CLERK_FRONTEND_API_URL", ""),
        },
    )


@router.post("/auth/session", status_code=204)
def create_session(
    request: Request,
    _: SameOrigin,
    db: DbSession,
):
    try:
        payload = verify_session_token(request)
    except ClerkConfigurationError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error

    clerk_user_id = payload.get("sub") if payload else None
    if not clerk_user_id:
        raise HTTPException(status_code=401, detail="Token de sessão inválido.")

    profile: dict[str, str | None] = {}
    try:
        profile = get_user_profile(clerk_user_id)
    except (ClerkApiError, ClerkConfigurationError):
        # Authentication must not fail just because profile enrichment is
        # temporarily unavailable; the Clerk webhook can fill it later.
        pass

    user = upsert_user(
        db,
        clerk_user_id,
        admin_user_id=os.getenv("CLERK_ADMIN_USER_ID"),
        email=profile.get("email"),
        first_name=profile.get("first_name"),
        last_name=profile.get("last_name"),
        image_url=profile.get("image_url"),
    )
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Este usuário está desativado.")

    request.session.clear()
    request.session["clerk_user_id"] = clerk_user_id
    return Response(status_code=204)


@router.delete("/auth/session", status_code=204)
def destroy_session(request: Request, _: SameOrigin):
    request.session.clear()
    return Response(status_code=204)


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return templates.TemplateResponse(
        "logout.html",
        {
            "request": request,
            "clerk_publishable_key": os.getenv("CLERK_PUBLISHABLE_KEY", ""),
            "clerk_frontend_api_url": os.getenv("CLERK_FRONTEND_API_URL", ""),
        },
    )
