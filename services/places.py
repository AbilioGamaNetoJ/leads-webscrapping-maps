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

# `websiteUri`, `internationalPhoneNumber` e `googleMapsUri` são campos da própria busca.
# Eles entram no mesmo SKU Enterprise que `rating`/`userRatingCount` já forçavam, então
# pedi-los aqui não muda o preço da chamada — e dispensa a chamada de Place Details, que
# custava US$ 0,020 por empresa e respondia por toda a fatura do projeto.
SEARCH_FIELD_MASK = (
    "places.id,places.displayName,places.formattedAddress,"
    "places.rating,places.userRatingCount,"
    "places.websiteUri,places.internationalPhoneNumber,places.googleMapsUri,"
    "nextPageToken"
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

# Numa região esgotada as ondas passam a voltar sem nenhum lugar inédito. Sem esta trava
# o lote seguiria pagando páginas até completar `MAX_WAVES_PER_BATCH`.
MAX_BARREN_WAVES = 3


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
    included_type: str | None,
    page_token: str | None,
) -> dict:
    response = await client.post(
        f"{PLACES_API_BASE}/places:searchText",
        headers={
            "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
            "X-Goog-FieldMask": SEARCH_FIELD_MASK,
        },
        # Sempre `PAGE_SIZE`: a página é cobrada por chamada, não por resultado, então
        # pedir menos que 20 paga o mesmo e colhe menos.
        json=build_search_body(
            text_query,
            rectangle,
            PAGE_SIZE,
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


def _passes_floors(place: dict, min_rating: float, min_reviews: int) -> bool:
    if min_rating > 0 and (place.get("rating") or 0) < min_rating:
        return False
    if min_reviews > 0 and (place.get("userRatingCount") or 0) < min_reviews:
        return False
    return True


async def _collect_batch(
    client: httpx.AsyncClient,
    db: Session,
    plan: tuple[SearchQuery, ...],
    rectangle: dict,
    batch_size: int,
    cursor: int,
    min_rating: float,
    min_reviews: int,
    only_without_website: bool = False,
) -> tuple[
    list[tuple[dict, SearchQuery]],
    list[tuple[dict, SearchQuery]],
    int,
    int,
    int | None,
]:
    """Consome o plano a partir de `cursor` até encher o lote ou esgotar as ondas.

    Devolve os aceitos e, à parte, os recusados pelo filtro de site: eles já foram pagos,
    então vão para o banco só para a deduplicação não pagar por eles de novo.
    """
    collected: list[tuple[dict, SearchQuery]] = []
    rejected: list[tuple[dict, SearchQuery]] = []
    seen_place_ids: set[str] = set()
    total_checked = 0
    skipped_duplicates = 0
    index = max(0, cursor)
    waves = 0
    barren_waves = 0

    while index < len(plan) and len(collected) < batch_size and waves < MAX_WAVES_PER_BATCH:
        remaining = batch_size - len(collected)
        # A onda é dimensionada pelo que falta, supondo a colheita típica de um termo
        # (uma página): larga o suficiente para o lote misturar nichos, estreita o
        # suficiente para não pagar por resultados que seriam descartados no corte.
        wave_size = min(QUERIES_PER_WAVE, max(2, math.ceil(remaining / PAGE_SIZE)))
        wave = plan[index : index + wave_size]
        index += len(wave)
        waves += 1

        # Uma página por termo por rodada, e só pagina de novo se o lote ainda estiver
        # faltando. Antes cada termo drenava as 3 páginas de uma vez, o que buscava até
        # 300 lugares para preencher 100 vagas — o excedente era descartado já pago.
        harvest: list[list[tuple[dict, SearchQuery]]] = [[] for _ in wave]
        tokens: list[str | None] = [None] * len(wave)
        active = list(range(len(wave)))

        for _ in range(MAX_PAGES_PER_QUERY):
            if not active:
                break

            pages = await asyncio.gather(
                *[
                    _fetch_search_page(
                        client, wave[i].text, rectangle, wave[i].included_type, tokens[i]
                    )
                    for i in active
                ]
            )

            still_active = []
            for i, page in zip(active, pages):
                places = page.get("places", [])
                total_checked += len(places)
                for place in places:
                    place_id = place.get("id")
                    if not place_id or place_id in seen_place_ids:
                        continue
                    seen_place_ids.add(place_id)
                    if not _passes_floors(place, min_rating, min_reviews):
                        continue
                    harvest[i].append((place, wave[i]))

                tokens[i] = page.get("nextPageToken")
                if tokens[i] and places:
                    still_active.append(i)

            active = still_active
            if sum(len(found) for found in harvest) >= remaining:
                break

        # Intercala os termos da onda: sem isso o corte por `batch_size` entregaria as
        # primeiras dezenas de linhas todas do mesmo nicho.
        candidates = [
            item
            for row in zip_longest(*harvest)
            for item in row
            if item is not None
        ]

        accepted_before = len(collected)
        known_ids = existing_place_ids(db, [place["id"] for place, _ in candidates])
        for place, query in candidates:
            if place["id"] in known_ids:
                skipped_duplicates += 1
                continue
            # O `websiteUri` agora vem na própria busca, então o filtro roda antes de a
            # linha ocupar uma vaga do lote. É o que faz "pedi 20" devolver 20 — antes o
            # corte acontecia depois do Details e encolhia o lote já pago.
            if only_without_website and place.get("websiteUri"):
                rejected.append((place, query))
                continue
            if len(collected) < batch_size:
                collected.append((place, query))

        barren_waves = 0 if len(collected) > accepted_before else barren_waves + 1
        if barren_waves >= MAX_BARREN_WAVES:
            break

    next_cursor = index if index < len(plan) else None
    return collected, rejected, total_checked, skipped_duplicates, next_cursor


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


async def _fill_missing_phones(
    client: httpx.AsyncClient, collected: list[tuple[dict, SearchQuery]]
) -> None:
    """Completa por Place Details só quem voltou da busca sem telefone.

    A busca já traz `internationalPhoneNumber`; esta chamada existe para os poucos casos
    em que o campo não vem preenchido. Antes era uma chamada paga por empresa.
    """
    pending = [place for place, _ in collected if not place.get("internationalPhoneNumber")]
    if not pending:
        return

    semaphore = asyncio.Semaphore(DETAILS_CONCURRENCY)

    async def fetch(place: dict) -> None:
        async with semaphore:
            try:
                details = await _fetch_details(client, place["id"])
            except Exception:
                return
        for field in ("internationalPhoneNumber", "websiteUri", "googleMapsUri"):
            if not place.get(field) and details.get(field):
                place[field] = details[field]

    await asyncio.gather(*[fetch(place) for place in pending])


def _to_business(place: dict, query: SearchQuery, has_website: bool) -> Business:
    return Business(
        place_id=place["id"],
        name=place.get("displayName", {}).get("text") or "Não informado",
        address=place.get("formattedAddress") or "Não informado",
        phone=place.get("internationalPhoneNumber") or "Não informado",
        maps_url=place.get("googleMapsUri") or "",
        has_website=has_website,
        rating=place.get("rating"),
        user_ratings_total=place.get("userRatingCount"),
        # Guarda a categoria real mesmo no modo "todos", para o histórico continuar filtrável.
        business_type=query.category_value,
    )


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
        collected, rejected, total_checked, skipped_duplicates, next_cursor = await _collect_batch(
            client,
            db,
            plan,
            rectangle,
            batch_size,
            cursor,
            min_rating,
            min_reviews,
            only_without_website,
        )

        await _fill_missing_phones(client, collected)

    results = []
    businesses = []
    with_website = len(rejected)
    without_website = 0

    for place, query in collected:
        has_website = bool(place.get("websiteUri"))
        if has_website:
            with_website += 1
        else:
            without_website += 1

        businesses.append(_to_business(place, query, has_website))
        results.append(
            {
                "name": businesses[-1].name,
                "address": businesses[-1].address,
                "phone": businesses[-1].phone,
                "maps_url": businesses[-1].maps_url,
                "has_website": has_website,
                "rating": place.get("rating"),
                "user_ratings_total": place.get("userRatingCount"),
            }
        )

    # Os recusados pelo filtro de site também vão para o banco. Sem isso a deduplicação
    # não os conhece e toda busca futura na mesma região volta a pagar por eles.
    persisted = businesses + [_to_business(place, query, True) for place, query in rejected]

    # Um commit por lote: contra o Postgres serverless, um commit por linha custaria
    # dezenas de segundos em buscas grandes.
    if persisted:
        db.add_all(persisted)
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
