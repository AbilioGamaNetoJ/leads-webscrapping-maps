import os
from typing import Annotated
from urllib.parse import urlsplit

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import AppUser
from services.users import get_user


class LoginRequired(Exception):
    def __init__(self, return_to: str):
        self.return_to = return_to


def is_safe_return_to(value: str | None) -> str:
    if not value:
        return "/"
    parsed = urlsplit(value)
    if parsed.scheme or parsed.netloc or not value.startswith("/") or value.startswith("//"):
        return "/"
    return value


DbSession = Annotated[Session, Depends(get_db)]


def get_current_user(request: Request, db: DbSession) -> AppUser:
    clerk_user_id = request.session.get("clerk_user_id")
    user = get_user(db, clerk_user_id) if clerk_user_id else None
    if user and user.is_active:
        return user

    request.session.clear()
    if request.url.path in {"/", "/historico", "/admin/users"}:
        raise LoginRequired(is_safe_return_to(request.url.path))
    raise HTTPException(status_code=401, detail="Autenticação necessária.")


CurrentUser = Annotated[AppUser, Depends(get_current_user)]


def require_admin(user: CurrentUser) -> AppUser:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso permitido apenas ao administrador.")
    return user


def require_same_origin(request: Request) -> None:
    origin = request.headers.get("origin")
    expected_origin = os.getenv("APP_URL", "").rstrip("/")
    if origin == expected_origin:
        return
    if os.getenv("APP_ENV") == "test" and not origin:
        return
    raise HTTPException(status_code=403, detail="Origem da requisição inválida.")
