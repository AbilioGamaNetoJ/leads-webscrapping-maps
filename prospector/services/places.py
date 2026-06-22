import asyncio
import httpx
import math
import os
from sqlalchemy.orm import Session
from database.models import Business
from services.geocoding import get_coordinates
from services.deduplication import place_id_exists
from dotenv import load_dotenv

load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
PLACES_API_BASE = "https://places.googleapis.com/v1"

CATEGORY_CONFIG: dict[str, dict] = {
    "restaurant": {
        "queries": ["restaurante", "hamburgueria", "pastelaria", "pizzaria", "lanchonete", "churrascaria"],
        "included_type": "restaurant",
    },
    "barber_shop": {
        "queries": ["barbearia"],
        "included_type": "barber_shop",
    },
    "beauty_salon": {
        "queries": ["salão de beleza", "cabeleireiro", "clínica de estética", "spa"],
        "included_type": "beauty_salon",
    },
    "pharmacy": {
        "queries": ["farmácia", "drogaria"],
        "included_type": "pharmacy",
    },
    "gym": {
        "queries": ["academia", "crossfit", "estúdio de pilates"],
        "included_type": "gym",
    },
    "pet_store": {
        "queries": ["pet shop", "casa de ração"],
        "included_type": "pet_store",
    },
    "doctor": {
        "queries": ["clínica médica", "consultório médico"],
        "included_type": "doctor",
    },
    "odontology": {
        "queries": ["dentista", "clínica odontológica", "ortodontista", "odontologia estética"],
        "included_type": "dental_clinic",
    },
    "aesthetics": {
        "queries": ["clínica de estética", "estética facial", "estética corporal", "spa", "dermatologia estética"],
        "included_type": "spa",
    },
    "lawyer": {
        "queries": ["advogado", "escritório de advocacia", "advocacia trabalhista", "advogado de família"],
        "included_type": "lawyer",
    },
    "accounting": {
        "queries": ["contabilidade", "escritório de contabilidade", "contador", "assessoria contábil"],
        "included_type": "accounting",
    },
    "real_estate": {
        "queries": ["imobiliária", "corretor de imóveis", "administradora de condomínios"],
        "included_type": "real_estate_agency",
    },
    "construction": {
        "queries": ["construtora", "empresa de reforma", "empreiteira", "escritório de arquitetura", "materiais de construção"],
        "included_type": "general_contractor",
    },
    "automotive": {
        "queries": ["oficina mecânica", "auto center", "funilaria e pintura", "auto peças", "borracharia", "estética automotiva"],
        "included_type": "car_repair",
    },
    "veterinary": {
        "queries": ["clínica veterinária", "hospital veterinário", "veterinário"],
        "included_type": "veterinary_care",
    },
    "furniture": {
        "queries": ["loja de móveis", "móveis planejados", "marcenaria", "decoração", "designer de interiores"],
        "included_type": "furniture_store",
    },
    "events": {
        "queries": ["salão de festas", "buffet", "organização de eventos", "locação de equipamentos para festas"],
        "included_type": "event_venue",
    },
    "education": {
        "queries": ["escola de idiomas", "autoescola", "escola de música", "reforço escolar", "escola infantil"],
        "included_type": "school",
    },
    "optics_jewelry": {
        "queries": ["ótica", "joalheria", "relojoaria"],
        "included_type": "jewelry_store", 
    },
    "solar_energy": {
        "queries": ["energia solar", "instalador de energia solar", "placas solares", "aquecedor solar"],
        "included_type": "electrician",
    },
    "insurance": {
        "queries": ["corretora de seguros", "seguros", "seguradora"],
        "included_type": "insurance_agency",
    },
    "clothing_store": {
        "queries": ["loja de roupas", "loja de calçados", "moda feminina", "moda infantil", "loja de departamento"],
        "included_type": "clothing_store",
    }
}

TYPE_LABEL_PT: dict[str, str] = {
    key: val["queries"][0] for key, val in CATEGORY_CONFIG.items()
}


def _circle_to_rectangle(lat: float, lng: float, radius_m: float) -> dict:
    delta_lat = radius_m / 111111
    delta_lng = radius_m / (111111 * math.cos(math.radians(lat)))
    return {
        "low":  {"latitude": lat - delta_lat, "longitude": lng - delta_lng},
        "high": {"latitude": lat + delta_lat, "longitude": lng + delta_lng},
    }

async def _fetch_places_for_query(client: httpx.AsyncClient, text_query: str, included_type: str | None, rectangle: dict, quantity: int) -> list:
    collected = []
    next_page_token = None
    while len(collected) < quantity:
        batch_size = min(20, quantity - len(collected))
        body = {
            "textQuery": text_query,
            "maxResultCount": batch_size,
            "locationRestriction": {"rectangle": rectangle},
        }
        if included_type:
            body["includedType"] = included_type
            body["strictTypeFiltering"] = True
            
        if next_page_token:
            body["pageToken"] = next_page_token

        response = await client.post(
            f"{PLACES_API_BASE}/places:searchText",
            headers={
                "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
                "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,nextPageToken",
            },
            json=body,
        )
        data = response.json()
        if "error" in data:
            err = data["error"]
            raise ValueError(
                f"Erro na Places API ({err.get('status', response.status_code)}): "
                f"{err.get('message', 'sem detalhe')}"
            )
        page_places = data.get("places", [])
        collected.extend(page_places)
        next_page_token = data.get("nextPageToken")
        if not next_page_token or not page_places:
            break
    return collected

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
    rectangle = _circle_to_rectangle(coords["lat"], coords["lng"], radius)

    cat_conf = CATEGORY_CONFIG.get(business_type, {"queries": [business_type], "included_type": business_type})
    queries = cat_conf["queries"]
    inc_type = cat_conf.get("included_type")

    # Para distribuir igualmente as buscas
    qty_per_query = math.ceil(quantity / len(queries))
    if qty_per_query < 1:
        qty_per_query = 1

    async with httpx.AsyncClient(timeout=30.0) as client:
        tasks = [
            _fetch_places_for_query(client, q, inc_type, rectangle, qty_per_query)
            for q in queries
        ]
        results_lists = await asyncio.gather(*tasks, return_exceptions=True)
        
        for res in results_lists:
            if isinstance(res, Exception):
                raise res

        mixed_places = []
        valid_lists = [res for res in results_lists if isinstance(res, list)]
        max_len = max((len(l) for l in valid_lists), default=0)
        for i in range(max_len):
            for l in valid_lists:
                if i < len(l):
                    mixed_places.append(l[i])
                    
        seen = set()
        unique_places = []
        for p in mixed_places:
            pid = p.get("id")
            if pid and pid not in seen:
                seen.add(pid)
                unique_places.append(p)
                
        collected_places = unique_places[:quantity]
        total_checked = len(collected_places)

        # 2. Filtra duplicatas antes de fazer chamadas de detalhes
        new_places = []
        skipped_duplicates = 0
        for place in collected_places:
            if place_id_exists(db, place["id"]):
                skipped_duplicates += 1
            else:
                new_places.append(place)

        # 3. Busca detalhes de todos em paralelo
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
        if not isinstance(details, dict):
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
            business_type=business_type,
        )
        db.add(business)
        db.commit()
        db.refresh(business)

        new_saved += 1
        results.append(
            {
                "id": business.id,
                "name": name,
                "address": address,
                "phone": phone,
                "maps_url": maps_url,
                "has_website": has_website,
                "business_type": business_type,
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
