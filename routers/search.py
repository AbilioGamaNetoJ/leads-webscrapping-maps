from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from database.connection import get_db
from services.places import search_businesses

router = APIRouter()


class SearchRequest(BaseModel):
    city: str = Field(..., min_length=1)
    neighborhood: str = Field("", min_length=0)
    business_type: str = Field(..., min_length=1)
    quantity: int = Field(..., ge=5, le=100)
    only_without_website: bool = False
    neighborhood_place_id: str = ""


@router.post("/search")
async def search(request: SearchRequest, db: Session = Depends(get_db)):
    try:
        return await search_businesses(
            db=db,
            city=request.city,
            neighborhood=request.neighborhood,
            business_type=request.business_type,
            quantity=request.quantity,
            only_without_website=request.only_without_website,
            neighborhood_place_id=request.neighborhood_place_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar negócios: {str(e)}")
