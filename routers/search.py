from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import AppUser
from services.auth import get_current_user, require_same_origin
from services.places import search_businesses

router = APIRouter()
DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[AppUser, Depends(get_current_user)]
SameOrigin = Annotated[None, Depends(require_same_origin)]


class SearchRequest(BaseModel):
    city: str = Field(..., min_length=1)
    neighborhood: str = Field("", min_length=0)
    business_type: str = Field(..., min_length=1)
    quantity: int = Field(..., ge=5, le=100)
    only_without_website: bool = False
    neighborhood_place_id: str = ""
    min_rating: float = Field(0, ge=0, le=5)
    min_reviews: int = Field(0, ge=0)


@router.post("/search")
async def search(
    request: SearchRequest,
    db: DbSession,
    _: CurrentUser,
    __: SameOrigin,
):
    try:
        return await search_businesses(
            db=db,
            city=request.city,
            neighborhood=request.neighborhood,
            business_type=request.business_type,
            quantity=request.quantity,
            only_without_website=request.only_without_website,
            neighborhood_place_id=request.neighborhood_place_id,
            min_rating=request.min_rating,
            min_reviews=request.min_reviews,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
