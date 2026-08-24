import asyncio
import math
import os
from itertools import zip_longest

import httpx
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from database.models import Business
from services.business_types import SearchQuery, resolve_search_plan
from services.deduplication import existing_place_ids
from services.geocoding import get_coordinates

load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
PLACES_API_BASE = "https://places.googleapis.com/v1"
SEARCH_FIELD_MASK = (
    "places.id,places.displayName,places.formattedAddress,"
    "places.rating,places.userRatingCount,nextPageToken"
)

# A Places API devolve no máximo 20 lugares por página e 3 páginas por consulta textual,
# ou seja 60 resultados por termo. Volumes altos só são possíveis somando muitos termos.
PAGE_SIZE = 20
MAX_PAGES_PER_QUERY = 3

# Cada lote roda dentro de uma request HTTP, que na Vercel Hobby morre em 10s.
QUERIES_PER_WAVE = 8
MAX_WAVES_PER_BATCH = 6
DETAILS_CONCURRENCY = 25
DEFAULT_BATCH_SIZE = 100


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


async def _drain_query(
    client: httpx.AsyncClient,
    query: SearchQuery,
    rectangle: dict,
    max_results: int,
) -> tuple[list[dict], int]:
    """Esgota um termo de busca, seguindo o nextPageToken até o limite da Places API.

    Esgotar cada termo dentro do lote é o que permite que o cursor entre lotes seja apenas
    um índice: nenhum pageToken precisa trafegar de volta pelo navegador.
    """
    places: list[dict] = []
    total_checked = 0
    page_token: str | None = None

    for _ in range(MAX_PAGES_PER_QUERY):
        page = await _fetch_search_page(
            client,
            query.text,
            rectangle,
            min(PAGE_SIZE, max(1, max_results - len(places))),
            query.included_type,
            page_token,
        )
        page_places = page.get("places", [])
        total_checked += len(page_places)
        places.extend(page_places)

        page_token = page.get("nextPageToken")
        if not page_token or not page_places or len(places) >= max_results:
            break

    return places, total_checked


async def _collect_batch(
    client: httpx.AsyncClient,
    db: Session,
    plan: tuple[SearchQuery, ...],
    rectangle: dict,
    batch_size: int,
    cursor: int,
    min_rating: float,
    min_reviews: int,
) -> tuple[list[tuple[dict, SearchQuery]], int, int, int | None]:
    """Consome o plano a partir de `cursor` até encher o lote ou esgotar as ondas."""
    collected: list[tuple[dict, SearchQuery]] = []
    seen_place_ids: set[str] = set()
    total_checked = 0
    skipped_duplicates = 0
    index = max(0, cursor)
    waves = 0

    while index < len(plan) and len(collected) < batch_size and waves < MAX_WAVES_PER_BATCH:
        remaining = batch_size - len(collected)
        # Cada termo é esgotado por inteiro — é o que mantém o cursor sendo só um índice.
        # A onda é dimensionada pelo que falta, supondo a colheita típica de um termo
        # (uma página): larga o suficiente para o lote misturar nichos, estreita o
        # suficiente para não pagar por resultados que seriam descartados no corte.
        wave_size = min(QUERIES_PER_WAVE, max(2, math.ceil(remaining / PAGE_SIZE)))
        wave = plan[index : index + wave_size]
        pages = await asyncio.gather(
            *[_drain_query(client, query, rectangle, remaining) for query in wave]
        )
        index += len(wave)
        waves += 1

        per_query: list[list[tuple[dict, SearchQuery]]] = []
        for query, (places, checked) in zip(wave, pages):
            total_checked += checked
            accepted: list[tuple[dict, SearchQuery]] = []
            for place in places:
                place_id = place.get("id")
                if not place_id or place_id in seen_place_ids:
                    continue
                seen_place_ids.add(place_id)
                if min_rating > 0 and (place.get("rating") or 0) < min_rating:
                    continue
                if min_reviews > 0 and (place.get("userRatingCount") or 0) < min_reviews:
                    continue
                accepted.append((place, query))
            per_query.append(accepted)

        # Intercala os termos da onda: sem isso o corte por `batch_size` entregaria as
        # primeiras dezenas de linhas todas do mesmo nicho.
        candidates = [
            item
            for row in zip_longest(*per_query)
            for item in row
            if item is not None
        ]

        known_ids = existing_place_ids(db, [place["id"] for place, _ in candidates])
        for place, query in candidates:
            if place["id"] in known_ids:
                skipped_duplicates += 1
            elif len(collected) < batch_size:
                collected.append((place, query))

    next_cursor = index if index < len(plan) else None
    return collected, total_checked, skipped_duplicates, next_cursor


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
    min_rating: float = 0,
    min_reviews: int = 0,
    cursor: int = 0,
    batch_size: int | None = None,
) -> dict:
    """Executa um lote da busca e devolve o cursor do próximo (None quando acabou)."""
    plan = resolve_search_plan(business_type)
    if not plan:
        raise ValueError("Tipo de negócio inválido.")

    batch_size = min(batch_size or DEFAULT_BATCH_SIZE, quantity)

    coords = await get_coordinates(city, neighborhood, neighborhood_place_id)
    radius = 2000.0 if (neighborhood.strip() or neighborhood_place_id) else 15000.0
    rectangle = _circle_to_rectangle(coords["lat"], coords["lng"], radius)

    async with httpx.AsyncClient(timeout=30.0) as client:
        collected, total_checked, skipped_duplicates, next_cursor = await _collect_batch(
            client,
            db,
            plan,
            rectangle,
            batch_size,
            cursor,
            min_rating,
            min_reviews,
        )

        details_semaphore = asyncio.Semaphore(DETAILS_CONCURRENCY)

        async def fetch_details(place_id: str) -> dict:
            async with details_semaphore:
                return await _fetch_details(client, place_id)

        details_list = await asyncio.gather(
            *[fetch_details(place["id"]) for place, _ in collected],
            return_exceptions=True,
        )

    results = []
    businesses = []
    with_website = 0
    without_website = 0

    for (place, query), details in zip(collected, details_list):
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
        address = place.get("formattedAddress") or "Não informado"
        phone = details.get("internationalPhoneNumber") or "Não informado"
        maps_url = details.get("googleMapsUri") or ""
        rating = place.get("rating")
        user_ratings_total = place.get("userRatingCount")

        businesses.append(
            Business(
                place_id=place["id"],
                name=name,
                address=address,
                phone=phone,
                maps_url=maps_url,
                has_website=has_website,
                rating=rating,
                user_ratings_total=user_ratings_total,
                # Guarda a categoria real mesmo no modo "todos", para o histórico continuar filtrável.
                business_type=query.category_value,
            )
        )
        results.append(
            {
                "name": name,
                "address": address,
                "phone": phone,
                "maps_url": maps_url,
                "has_website": has_website,
                "rating": rating,
                "user_ratings_total": user_ratings_total,
            }
        )

    # Um commit por lote: contra o Postgres serverless, um commit por linha custaria
    # dezenas de segundos em buscas grandes.
    if businesses:
        db.add_all(businesses)
        db.commit()

    return {
        "results": results,
        "cursor": next_cursor,
        "summary": {
            "total_checked": total_checked,
            "new_saved": len(businesses),
            "skipped_duplicates": skipped_duplicates,
            "with_website": with_website,
            "without_website": without_website,
        },
    }
