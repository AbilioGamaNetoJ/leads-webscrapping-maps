"""Compara os campos do Text Search com os do Place Details para os mesmos lugares.

Motivo: o Place Details responde por 100% da fatura do projeto (1 chamada por empresa),
e `websiteUri`/`internationalPhoneNumber`/`googleMapsUri` já são campos suportados pelo
Text Search — no mesmo SKU Enterprise que a busca já paga por causa de `rating` e
`userRatingCount`. Se a busca entregar os mesmos dados, o Details vira supérfluo.

Este script mede isso com dados reais antes de a gente confiar na troca.

Uso:
    GOOGLE_MAPS_API_KEY=... python scripts/validate_search_fields.py "Florianópolis" "Centro" "Marceneiro" [--details N]

A busca é sempre uma só, devolvendo até 20 negócios. `--details N` diz quantos DESSES
negócios recebem uma segunda chamada (Place Details) para conferir campo a campo — não
altera quantos negócios são buscados. Padrão 5; use 0 para pular a conferência.

O número de chamadas é fixo: 1 Geocoding + 1 Text Search + N Place Details. Não há laço
nem paginação, então não existe cenário de consumo descontrolado.

Custo por execução, a R$ 0,18 por busca e R$ 0,103 por Details:
    --details 0   ->  ~R$ 0,21   confirma que o field mask é aceito e que os campos vêm
    --details 5   ->  ~R$ 0,72   amostra para detectar divergência sistemática (padrão)
    --details 20  ->  ~R$ 2,27   confere todos os 20 negócios da busca
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


async def main(city: str, neighborhood: str, term: str, n_details: int) -> int:
    if not API_KEY:
        print("Defina GOOGLE_MAPS_API_KEY no ambiente.")
        return 1

    estimate = 0.026 + 0.18 + n_details * 0.103
    print(f"Busca: 1 chamada, até 20 negócios.")
    print(f"Conferência: {n_details} Place Details.")
    print(f"Custo estimado: R$ {estimate:.2f}\n")

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

        sampled = places[:n_details]
        details = await asyncio.gather(
            *[
                client.get(
                    f"{PLACES_API_BASE}/places/{place['id']}",
                    headers={"X-Goog-Api-Key": API_KEY, "X-Goog-FieldMask": DETAILS_MASK},
                )
                for place in sampled
            ]
        )

    # A busca sozinha já responde a pergunta mais importante: o field mask foi aceito e os
    # campos vêm preenchidos. A comparação com o Details mede completude, que é o risco fino.
    filled_site = sum(1 for p in places if p.get("websiteUri"))
    filled_phone = sum(1 for p in places if p.get("internationalPhoneNumber"))
    print(f"Da busca: {filled_site}/{len(places)} com websiteUri, "
          f"{filled_phone}/{len(places)} com telefone.\n")

    if not sampled:
        print("Sem comparação com Place Details (n_details=0).")
        return 0

    divergences = 0
    search_phone = search_site = details_phone = details_site = 0

    for place, response in zip(sampled, details):
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

    total = len(sampled)
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


def parse_args(argv: list[str]) -> tuple[str, str, str, int]:
    """Cidade, bairro, termo e quantos Place Details conferir.

    `--details` é flag nomeada de propósito: um número solto no fim da linha se confunde
    com "quantos negócios buscar", que não é o que ele controla.
    """
    n_details = 5
    positional: list[str] = []
    index = 0
    while index < len(argv):
        if argv[index] == "--details":
            n_details = int(argv[index + 1])
            index += 2
            continue
        positional.append(argv[index])
        index += 1

    return (
        positional[0] if positional else "Florianópolis",
        positional[1] if len(positional) > 1 else "Centro",
        positional[2] if len(positional) > 2 else "Marceneiro",
        n_details,
    )


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main(*parse_args(sys.argv[1:]))))
