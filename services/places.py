import asyncio
import math
import os

import httpx
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from database.models import Business
from services.business_types import BusinessType, get_business_type
from services.deduplication import place_id_exists
from services.geocoding import get_coordinates

load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
PLACES_API_BASE = "https://places.googleapis.com/v1"
SEARCH_FIELD_MASK = "places.id,places.displayName,places.formattedAddress,nextPageToken"


def _circle_to_rectangle(lat: float, lng: float, radius_m: float) -> dict:
    delta_lat = radius_m / 111111
    delta_lng = radius_m / (111111 * math.cos(math.radians(lat)))
    return {
        "low": {"latitude": lat - delta_lat, "longitude": lng - delta_lng},
        "high": {"latitude": lat + delta_lat, "longitude": lng + delta_lng},
    }


def build_search_body(
    text_query: str,
    rectangle: dict,
    max_results: int,
    included_type: str | None = None,
    page_token: str | None = None,
) -> dict:
    body = {
        "textQuery": text_query,
        "maxResultCount": max_results,
        "locationRestriction": {"rectangle": rectangle},
    }
    if included_type:
        body.update({"includedType": included_type, "strictTypeFiltering": True})
    if page_token:
        body["pageToken"] = page_token
    return body


async def _fetch_search_page(
    client: httpx.AsyncClient,
    text_query: str,
    rectangle: dict,
    max_results: int,
    included_type: str | None,
    page_token: str | None,
) -> dict:
    response = await client.post(
        f"{PLACES_API_BASE}/places:searchText",
        headers={
            "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
            "X-Goog-FieldMask": SEARCH_FIELD_MASK,
        },
        json=build_search_body(
            text_query,
            rectangle,
            max_results,
            included_type,
            page_token,
        ),
    )
    data = response.json()
    if "error" in data:
        error = data["error"]
        raise ValueError(
            f"Erro na Places API ({error.get('status', response.status_code)}): "
            f"{error.get('message', 'sem detalhe')}"
        )
    return data


async def _fetch_category_places(
    client: httpx.AsyncClient,
    category: BusinessType,
    rectangle: dict,
    quantity: int,
) -> tuple[list[dict], int]:
    pending_queries = {query: None for query in category.search_terms}
    collected_places: list[dict] = []
    seen_place_ids: set[str] = set()
    total_checked = 0

    while pending_queries and len(collected_places) < quantity:
        remaining = quantity - len(collected_places)
        page_size = min(20, max(1, math.ceil(remaining / len(pending_queries))))
        pages = await asyncio.gather(
            *[
                _fetch_search_page(
                    client,
                    query,
                    rectangle,
                    page_size,
                    category.included_type,
                    page_token,
                )
                for query, page_token in pending_queries.items()
            ]
        )

        next_queries: dict[str, str] = {}
        for (query, _), page in zip(pending_queries.items(), pages):
            page_places = page.get("places", [])
            total_checked += len(page_places)
            for place in page_places:
                place_id = place.get("id")
                if place_id and place_id not in seen_place_ids:
                    seen_place_ids.add(place_id)
                    collected_places.append(place)
                    if len(collected_places) == quantity:
                        break

            next_page_token = page.get("nextPageToken")
            if next_page_token and page_places:
                next_queries[query] = next_page_token
            if len(collected_places) == quantity:
                break

        pending_queries = next_queries

    return collected_places, total_checked


async def _fetch_details(client: httpx.AsyncClient, place_id: str) -> dict:
    response = await client.get(
        f"{PLACES_API_BASE}/places/{place_id}",
        headers={
            "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
            "X-Goog-FieldMask": "internationalPhoneNumber,websiteUri,googleMapsUri",
        },
    )
    response.raise_for_status()
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
    category = get_business_type(business_type)
    if not category:
        raise ValueError("Tipo de negócio inválido.")

    coords = await get_coordinates(city, neighborhood, neighborhood_place_id)
    radius = 2000.0 if (neighborhood.strip() or neighborhood_place_id) else 15000.0
    rectangle = _circle_to_rectangle(coords["lat"], coords["lng"], radius)

    async with httpx.AsyncClient(timeout=30.0) as client:
        collected_places, total_checked = await _fetch_category_places(
            client,
            category,
            rectangle,
            quantity,
        )

        new_places = []
        skipped_duplicates = 0
        for place in collected_places:
            place_id = place.get("id")
            if not place_id:
                continue
            if place_id_exists(db, place_id):
                skipped_duplicates += 1
            else:
                new_places.append(place)

        details_list = await asyncio.gather(
            *[_fetch_details(client, place["id"]) for place in new_places],
            return_exceptions=True,
        )

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

        name = place.get("displayName", {}).get("text") or "Não informado"
        business = Business(
            place_id=place["id"],
            name=name,
            address=place.get("formattedAddress") or "Não informado",
            phone=details.get("internationalPhoneNumber") or "Não informado",
            maps_url=details.get("googleMapsUri") or "",
            has_website=has_website,
            business_type=category.value,
        )
        db.add(business)
        db.commit()
        db.refresh(business)

        new_saved += 1
        results.append(
            {
                "name": name,
                "address": business.address,
                "phone": business.phone,
                "maps_url": business.maps_url,
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
