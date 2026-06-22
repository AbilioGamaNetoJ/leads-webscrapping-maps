from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from database.connection import get_db
from database.models import Business
from services.xlsx_generator import generate_xlsx

router = APIRouter()


@router.get("/export")
def export(only_without_website: bool = False, ids: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Business)
    
    if ids is not None:
        id_list = [int(i) for i in ids.split(",") if i.strip().isdigit()]
        if id_list:
            query = query.filter(Business.id.in_(id_list))
        else:
            query = query.filter(Business.id == -1)
    elif only_without_website:
        query = query.filter(Business.has_website == False)

    businesses = query.order_by(Business.created_at.desc()).all()
    xlsx = generate_xlsx(businesses)

    return StreamingResponse(
        xlsx,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=negocios-prospectados.xlsx"},
    )
