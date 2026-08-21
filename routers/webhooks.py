import json
import os
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from database.connection import get_db
from services.clerk import ClerkConfigurationError
from services.users import deactivate_user, upsert_user

router = APIRouter(tags=["webhooks"])
DbSession = Annotated[Session, Depends(get_db)]


def _primary_email(payload: dict[str, Any]) -> str | None:
    primary_id = payload.get("primary_email_address_id")
    for email in payload.get("email_addresses", []):
        if email.get("id") == primary_id:
            return email.get("email_address")
    return None


def _verify_event(body: bytes, headers: dict[str, str]) -> dict[str, Any]:
    try:
        from svix.webhooks import Webhook
    except ImportError as error:
        raise ClerkConfigurationError("A dependência svix não está instalada.") from error

    secret = os.getenv("CLERK_WEBHOOK_SIGNING_SECRET")
    if not secret:
        raise ClerkConfigurationError("A variável CLERK_WEBHOOK_SIGNING_SECRET não está configurada.")
    Webhook(secret).verify(body, headers)
    return json.loads(body)


@router.post("/webhooks/clerk", status_code=204)
async def clerk_webhook(request: Request, db: DbSession):
    headers = {
        header: request.headers[header]
        for header in ("svix-id", "svix-timestamp", "svix-signature")
        if header in request.headers
    }
    try:
        event = _verify_event(await request.body(), headers)
    except ClerkConfigurationError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=400, detail="Assinatura de webhook inválida.") from error

    payload = event.get("data", {})
    clerk_user_id = payload.get("id")
    if not clerk_user_id:
        return

    if event.get("type") == "user.deleted":
        deactivate_user(db, clerk_user_id)
        return

    if event.get("type") in {"user.created", "user.updated"}:
        upsert_user(
            db,
            clerk_user_id,
            admin_user_id=os.getenv("CLERK_ADMIN_USER_ID"),
            email=_primary_email(payload),
            first_name=payload.get("first_name"),
            last_name=payload.get("last_name"),
            image_url=payload.get("image_url"),
        )
