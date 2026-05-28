from pathlib import Path
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database.connection import get_db
from database.models import Business

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))


class DeleteRequest(BaseModel):
    ids: list[int]


@router.delete("/historico")
def delete_businesses(payload: DeleteRequest, db: Session = Depends(get_db)):
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
    db: Session = Depends(get_db),
):
    query = db.query(Business)

    if name:
        query = query.filter(Business.name.ilike(f"%{name}%"))

    if has_website == "true":
        query = query.filter(Business.has_website == True)
    elif has_website == "false":
        query = query.filter(Business.has_website == False)

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
        },
    )
