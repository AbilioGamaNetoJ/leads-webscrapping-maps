import httpx
import os
from fastapi import APIRouter, Query
from dotenv import load_dotenv

load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

router = APIRouter()


@router.get("/autocomplete")
async def autocomplete(
    input: str = Query(..., min_length=2),
    kind: str = Query("city"),
    city: str = Query(""),
):
    url = "https://maps.googleapis.com/maps/api/place/autocomplete/json"

    if kind == "city":
        params = {
            "input": input,
            "types": "(cities)",
            "components": "country:br",
            "language": "pt-BR",
            "key": GOOGLE_MAPS_API_KEY,
        }
    else:
        query = f"{input}, {city}" if city.strip() else input
        params = {
            "input": query,
            "types": "sublocality",
            "language": "pt-BR",
            "key": GOOGLE_MAPS_API_KEY,
        }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()

    suggestions = []
    for pred in data.get("predictions", []):
        suggestions.append({
            "label": pred["description"],
            "value": pred["structured_formatting"]["main_text"],
            "place_id": pred.get("place_id", ""),
        })

    return {"suggestions": suggestions[:6]}
