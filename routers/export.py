from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import AppUser, Business
from services.auth import get_current_user
from services.business_filters import apply_business_filters
from services.xlsx_generator import generate_xlsx

router = APIRouter()
DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[AppUser, Depends(get_current_user)]


@router.get("/export")
def export(
    db: DbSession,
    _: CurrentUser,
    ids: Annotated[list[int] | None, Query()] = None,
    name: str = "",
    has_website: str = "",
    business_type: str = "",
    only_without_website: bool = False,
):
    query = db.query(Business)
    if only_without_website:
        has_website = "false"

    query = apply_business_filters(
        query,
        name=name,
        has_website=has_website,
        business_type=business_type,
    )
    if ids is not None:
        query = query.filter(Business.id.in_(ids))

    businesses = query.order_by(Business.created_at.desc(), Business.id.desc()).all()
    xlsx = generate_xlsx(businesses)

    return Response(
        content=xlsx.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=negocios-prospectados.xlsx"},
    )
