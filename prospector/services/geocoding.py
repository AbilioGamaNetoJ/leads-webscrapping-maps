import httpx
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")


async def get_coordinates(city: str, neighborhood: str, place_id: str = "") -> dict:
    url = "https://maps.googleapis.com/maps/api/geocode/json"

    async with httpx.AsyncClient() as client:
        if place_id:
            params = {"place_id": place_id, "key": GOOGLE_MAPS_API_KEY}
        elif neighborhood.strip():
            params = {"address": f"{neighborhood}, {city}, Brasil", "key": GOOGLE_MAPS_API_KEY}
        else:
            params = {"address": f"{city}, Brasil", "key": GOOGLE_MAPS_API_KEY}

        response = await client.get(url, params=params)
        data = response.json()

    if data.get("status") != "OK" or not data.get("results"):
        api_status = data.get("status", "UNKNOWN")
        location = f"{neighborhood}, {city}" if neighborhood.strip() else city
        raise ValueError(
            f"Não foi possível localizar coordenadas para: {location} "
            f"(status da API: {api_status})"
        )

    location = data["results"][0]["geometry"]["location"]
    return {"lat": location["lat"], "lng": location["lng"]}
