import asyncio
import httpx
import os
from sqlalchemy.orm import Session
from database.models import Business
from services.geocoding import get_coordinates
from services.deduplication import place_id_exists
from dotenv import load_dotenv

load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
PLACES_API_BASE = "https://places.googleapis.com/v1"

# A API do Google nem sempre classifica com o tipo esperado; mapeamos para cobrir sinônimos reais.
# Tipos válidos: https://developers.google.com/maps/documentation/places/web-service/place-types
# Apenas tipos da Table A da Places API (New) confirmados para searchNearby.
# meal_delivery / meal_takeaway são tipos de serviço, não de local físico — causam INVALID_ARGUMENT.
INCLUDED_TYPES_MAP: dict[str, list[str]] = {
    "restaurant": [
        "restaurant",
        "fast_food_restaurant",
        "brazilian_restaurant",
        "barbecue_restaurant",
        "hamburger_restaurant",
        "pizza_restaurant",
        "seafood_restaurant",
        "steak_house",
        "sandwich_shop",
    ],
    "barber_shop": [
        "barber_shop",
    ],
    "clothing_store": [
        "clothing_store",
        "shoe_store",
        "department_store",
    ],
    "beauty_salon": [
        "beauty_salon",
        "hair_salon",
        "nail_salon",
        "spa",
    ],
    "pharmacy": [
        "pharmacy",
        "drugstore",
    ],
    "bakery": [
        "bakery",
        "cafe",
    ],
    "gym": [
        "gym",
        "fitness_center",
        "sports_club",
        "yoga_studio",
    ],
    "supermarket": [
        "supermarket",
        "grocery_store",
        "hypermarket",
        "convenience_store",
    ],
    "pet_store": [
        "pet_store",
        "veterinary_care",
    ],
    "doctor": [
        "doctor",
        "medical_clinic",
        "dentist",
        "dental_clinic",
        "physiotherapist",
    ],
}


async def _fetch_details(client: httpx.AsyncClient, place_id: str) -> dict:
    response = await client.get(
        f"{PLACES_API_BASE}/places/{place_id}",
        headers={
            "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
            "X-Goog-FieldMask": "internationalPhoneNumber,websiteUri,googleMapsUri",
        },
    )
    return response.json()


async def search_businesses(
    db: Session,
    city: str,
    neighborhood: str,
    business_type: str,
    quantity: int,
    only_without_website: bool,
    neighborhood_place_id: str = "",
) -> dict:
    coords = await get_coordinates(city, neighborhood, neighborhood_place_id)
    radius = 2000.0 if (neighborhood.strip() or neighborhood_place_id) else 15000.0

    api_types = INCLUDED_TYPES_MAP.get(business_type, [business_type])
    # searchNearby não suporta paginação — máximo 20 por chamada
    batch_size = min(20, quantity)

    async with httpx.AsyncClient(timeout=30.0) as client:
        nearby_response = await client.post(
            f"{PLACES_API_BASE}/places:searchNearby",
            headers={
                "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
                "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress",
            },
            json={
                "includedPrimaryTypes": api_types,
                "maxResultCount": batch_size,
                "locationRestriction": {
                    "circle": {
                        "center": {"latitude": coords["lat"], "longitude": coords["lng"]},
                        "radius": radius,
                    }
                },
            },
        )
        nearby_data = nearby_response.json()
        if "error" in nearby_data:
            err = nearby_data["error"]
            raise ValueError(
                f"Erro na Places API ({err.get('status', nearby_response.status_code)}): "
                f"{err.get('message', 'sem detalhe')}"
            )
        collected_places = nearby_data.get("places", [])
        total_checked = len(collected_places)

        # 2. Filtra duplicatas antes de fazer chamadas de detalhes
        new_places = []
        skipped_duplicates = 0
        for place in collected_places:
            if not place.get("id"):
                continue
            if place_id_exists(db, place["id"]):
                skipped_duplicates += 1
            else:
                new_places.append(place)

        # 3. Busca detalhes de todos em paralelo — transforma N requisições sérias em ~1 round-trip
        details_list = await asyncio.gather(
            *[_fetch_details(client, p["id"]) for p in new_places],
            return_exceptions=True,
        )

    # 4. Processa resultados e salva no banco
    results = []
    new_saved = 0
    with_website = 0
    without_website = 0

    for place, details in zip(new_places, details_list):
        if isinstance(details, Exception):
            continue

        has_website = bool(details.get("websiteUri"))

        if only_without_website and has_website:
            with_website += 1
            continue

        if has_website:
            with_website += 1
        else:
            without_website += 1

        phone = details.get("internationalPhoneNumber") or "Não informado"
        maps_url = details.get("googleMapsUri") or ""
        name = place.get("displayName", {}).get("text") or "Não informado"
        address = place.get("formattedAddress") or "Não informado"

        business = Business(
            place_id=place["id"],
            name=name,
            address=address,
            phone=phone,
            maps_url=maps_url,
            has_website=has_website,
        )
        db.add(business)
        db.commit()
        db.refresh(business)

        new_saved += 1
        results.append(
            {
                "name": name,
                "address": address,
                "phone": phone,
                "maps_url": maps_url,
                "has_website": has_website,
            }
        )

    return {
        "results": results,
        "summary": {
            "total_checked": total_checked,
            "new_saved": new_saved,
            "skipped_duplicates": skipped_duplicates,
            "with_website": with_website,
            "without_website": without_website,
        },
    }
