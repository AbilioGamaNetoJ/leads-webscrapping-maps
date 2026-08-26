"""Compara os campos do Text Search com os do Place Details para os mesmos lugares.

Motivo: o Place Details responde por 100% da fatura do projeto (1 chamada por empresa),
e `websiteUri`/`internationalPhoneNumber`/`googleMapsUri` já são campos suportados pelo
Text Search — no mesmo SKU Enterprise que a busca já paga por causa de `rating` e
`userRatingCount`. Se a busca entregar os mesmos dados, o Details vira supérfluo.

Este script mede isso com dados reais antes de a gente confiar na troca.

Uso:
    GOOGLE_MAPS_API_KEY=... python scripts/validate_search_fields.py "Florianópolis" "Centro" "Marceneiro"

Custo de uma execução: 1 página de Text Search (~R$ 0,18) + até 20 Place Details
(~R$ 0,10 cada) ≈ R$ 2,25. É pago uma vez para evitar uma migração às cegas.
"""

import asyncio
import os
import sys

import httpx

PLACES_API_BASE = "https://places.googleapis.com/v1"
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# O mask proposto: o de hoje mais os três campos que hoje custam uma chamada de Details.
SEARCH_MASK = (
    "places.id,places.displayName,places.formattedAddress,"
    "places.rating,places.userRatingCount,"
    "places.websiteUri,places.internationalPhoneNumber,places.googleMapsUri"
)
DETAILS_MASK = "internationalPhoneNumber,websiteUri,googleMapsUri"


async def main(city: str, neighborhood: str, term: str) -> int:
    if not API_KEY:
        print("Defina GOOGLE_MAPS_API_KEY no ambiente.")
        return 1

    async with httpx.AsyncClient(timeout=30.0) as client:
        geo = await client.get(
            "https://maps.googleapis.com/maps/api/geocode/json",
            params={"address": f"{neighborhood}, {city}, Brasil".strip(", "), "key": API_KEY},
        )
        geo_data = geo.json()
        if geo_data.get("status") != "OK":
            print(f"Geocoding falhou: {geo_data.get('status')}")
            return 1
        loc = geo_data["results"][0]["geometry"]["location"]

        delta = 2000 / 111111
        search = await client.post(
            f"{PLACES_API_BASE}/places:searchText",
            headers={"X-Goog-Api-Key": API_KEY, "X-Goog-FieldMask": SEARCH_MASK},
            json={
                "textQuery": term,
                "maxResultCount": 20,
                "locationRestriction": {
                    "rectangle": {
                        "low": {"latitude": loc["lat"] - delta, "longitude": loc["lng"] - delta},
                        "high": {"latitude": loc["lat"] + delta, "longitude": loc["lng"] + delta},
                    }
                },
            },
        )
        payload = search.json()
        if "error" in payload:
            print(f"Text Search recusou o field mask: {payload['error'].get('message')}")
            print("=> Se a recusa citar um campo, ele NÃO é suportado na busca.")
            return 1

        places = payload.get("places", [])
        if not places:
            print("A busca não devolveu lugares. Tente outro termo/bairro.")
            return 1

        print(f"Text Search aceitou o field mask e devolveu {len(places)} lugares.\n")

        details = await asyncio.gather(
            *[
                client.get(
                    f"{PLACES_API_BASE}/places/{place['id']}",
                    headers={"X-Goog-Api-Key": API_KEY, "X-Goog-FieldMask": DETAILS_MASK},
                )
                for place in places
            ]
        )

    divergences = 0
    search_phone = search_site = details_phone = details_site = 0

    for place, response in zip(places, details):
        detail = response.json()
        name = place.get("displayName", {}).get("text", place["id"])

        s_site, d_site = place.get("websiteUri"), detail.get("websiteUri")
        s_phone, d_phone = place.get("internationalPhoneNumber"), detail.get("internationalPhoneNumber")

        search_site += bool(s_site)
        details_site += bool(d_site)
        search_phone += bool(s_phone)
        details_phone += bool(d_phone)

        # A divergência que importa é a de site: ela decide se o lead entra como
        # "sem site", que é o filtro central do produto.
        if bool(s_site) != bool(d_site):
            divergences += 1
            print(f"  [SITE DIVERGE] {name}: busca={s_site!r} details={d_site!r}")
        if bool(s_phone) != bool(d_phone):
            print(f"  [telefone difere] {name}: busca={s_phone!r} details={d_phone!r}")

    total = len(places)
    print(f"\n{'':<22}{'busca':>8}{'details':>10}")
    print(f"{'com websiteUri':<22}{search_site:>8}{details_site:>10}  (de {total})")
    print(f"{'com telefone':<22}{search_phone:>8}{details_phone:>10}  (de {total})")
    print(f"\nDivergências de site: {divergences}/{total}")

    if divergences == 0 and search_phone >= details_phone:
        print("\nOK: a busca entrega o mesmo que o Details. Dá para eliminar a chamada.")
    elif divergences == 0:
        print(f"\nOK para site. {details_phone - search_phone} lugar(es) só têm telefone via")
        print("Details — o fallback por telefone ausente cobre esse caso.")
    else:
        print("\nATENÇÃO: houve divergência de site. Não confie só na busca para esse filtro.")
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    city = args[0] if args else "Florianópolis"
    neighborhood = args[1] if len(args) > 1 else "Centro"
    term = args[2] if len(args) > 2 else "Marceneiro"
    raise SystemExit(asyncio.run(main(city, neighborhood, term)))
