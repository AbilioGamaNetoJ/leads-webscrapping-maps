import os
from pathlib import Path
from typing import Annotated
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import EmailStr
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import AppUser
from services.auth import require_admin, require_same_origin
from services.clerk import (
    ClerkApiError,
    ClerkConfigurationError,
    create_invitation,
    list_pending_invitations,
    revoke_invitation,
)
from services.users import set_user_active

router = APIRouter(prefix="/admin", tags=["users"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))
DbSession = Annotated[Session, Depends(get_db)]
AdminUser = Annotated[AppUser, Depends(require_admin)]


def _redirect_with_notice(message: str) -> RedirectResponse:
    return RedirectResponse(f"/admin/users?{urlencode({'notice': message})}", status_code=303)


@router.get("/users")
def users_page(request: Request, admin: AdminUser, db: DbSession, notice: str = ""):
    pending_invitations = []
    invitation_error = ""
    try:
        pending_invitations = list_pending_invitations()
    except (ClerkApiError, ClerkConfigurationError):
        invitation_error = "Não foi possível carregar os convites pendentes agora."

    users = db.query(AppUser).order_by(AppUser.created_at.asc()).all()
    return templates.TemplateResponse(
        "users.html",
        {
            "request": request,
            "current_user": admin,
            "users": users,
            "pending_invitations": pending_invitations,
            "notice": notice,
            "invitation_error": invitation_error,
        },
    )


@router.post("/users/invitations")
def invite_user(
    email: Annotated[EmailStr, Form()],
    _: Annotated[None, Depends(require_same_origin)],
    admin: AdminUser,
):
    try:
        create_invitation(str(email), f"{os.getenv('APP_URL', '').rstrip('/')}/auth/complete")
    except (ClerkApiError, ClerkConfigurationError):
        return _redirect_with_notice("Não foi possível enviar o convite. Tente novamente.")
    return _redirect_with_notice("Convite enviado com sucesso.")


@router.post("/users/{clerk_user_id}/status")
def update_user_status(
    clerk_user_id: str,
    is_active: Annotated[bool, Form()],
    _: Annotated[None, Depends(require_same_origin)],
    admin: AdminUser,
    db: DbSession,
):
    if clerk_user_id == admin.clerk_user_id and not is_active:
        raise HTTPException(status_code=400, detail="O administrador não pode desativar a própria conta.")

    user = set_user_active(db, clerk_user_id, is_active)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    return _redirect_with_notice("Acesso do usuário atualizado.")


@router.post("/invitations/{invitation_id}/revoke")
def revoke_user_invitation(
    invitation_id: str,
    _: Annotated[None, Depends(require_same_origin)],
    admin: AdminUser,
):
    try:
        revoke_invitation(invitation_id)
    except (ClerkApiError, ClerkConfigurationError):
        return _redirect_with_notice("Não foi possível revogar o convite. Tente novamente.")
    return _redirect_with_notice("Convite revogado.")
