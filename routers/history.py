from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import AppUser, Business
from services.auth import get_current_user, require_admin, require_same_origin
from services.business_types import as_dicts, type_labels
from services.whatsapp import to_whatsapp_url

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))
templates.env.filters["whatsapp_url"] = to_whatsapp_url
DbSession = Annotated[Session, Depends(get_db)]
AdminUser = Annotated[AppUser, Depends(require_admin)]
CurrentUser = Annotated[AppUser, Depends(get_current_user)]
SameOrigin = Annotated[None, Depends(require_same_origin)]


class DeleteRequest(BaseModel):
    ids: list[int]


@router.delete("/historico")
def delete_businesses(
    payload: DeleteRequest,
    db: DbSession,
    _: AdminUser,
    __: SameOrigin,
):
    if not payload.ids:
        raise HTTPException(status_code=400, detail="Nenhum ID informado.")
    deleted = db.query(Business).filter(Business.id.in_(payload.ids)).delete(synchronize_session=False)
    db.commit()
    return {"deleted": deleted}

PER_PAGE = 20


@router.get("/historico")
def history(
    request: Request,
    page: int = 1,
    name: str = "",
    has_website: str = "",
    business_type: str = "",
    *,
    db: DbSession,
    current_user: CurrentUser,
):
    query = db.query(Business)

    if name:
        query = query.filter(Business.name.ilike(f"%{name}%"))

    if has_website == "true":
        query = query.filter(Business.has_website == True)
    elif has_website == "false":
        query = query.filter(Business.has_website == False)

    if business_type:
        query = query.filter(Business.business_type == business_type)

    total = query.count()
    businesses = (
        query.order_by(Business.created_at.desc())
        .offset((page - 1) * PER_PAGE)
        .limit(PER_PAGE)
        .all()
    )
    total_pages = max(1, (total + PER_PAGE - 1) // PER_PAGE)

    return templates.TemplateResponse(
        "historico.html",
        {
            "request": request,
            "businesses": businesses,
            "page": page,
            "total_pages": total_pages,
            "total": total,
            "name": name,
            "has_website": has_website,
            "business_type": business_type,
            "business_types": as_dicts(),
            "type_labels": type_labels(),
            "current_user": current_user,
        },
    )
