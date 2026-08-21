from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import AppUser, Business
from services.auth import get_current_user
from services.xlsx_generator import generate_xlsx

router = APIRouter()
DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[AppUser, Depends(get_current_user)]


@router.get("/export")
def export(
    db: DbSession,
    _: CurrentUser,
    only_without_website: bool = False,
):
    query = db.query(Business)
    if only_without_website:
        query = query.filter(Business.has_website == False)

    businesses = query.order_by(Business.created_at.desc()).all()
    xlsx = generate_xlsx(businesses)

    return StreamingResponse(
        xlsx,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=negocios-prospectados.xlsx"},
    )
