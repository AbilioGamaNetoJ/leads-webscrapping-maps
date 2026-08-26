"""Cobre o que mudou por causa do custo da Places API.

O Place Details respondia por 100% da fatura (uma chamada paga por empresa) e a busca
pagava páginas que eram descartadas. Estes testes travam as três decisões que resolveram
isso: os campos vêm da busca, a página é sempre cheia, e o filtro de site roda antes de o
lote fechar.
"""

import asyncio
import unittest

from services.business_types import resolve_search_plan
from services.places import (
    MAX_BARREN_WAVES,
    PAGE_SIZE,
    SEARCH_FIELD_MASK,
    _collect_batch,
    _fill_missing_phones,
)


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload
        self.status_code = 200

    def json(self):
        return self.payload

    def raise_for_status(self):
        return None


class FakeSearchClient:
    """Devolve `per_query` lugares por termo, alternando quem tem site."""

    def __init__(self, per_query=2, with_site_every=0, page_token=None, empty=False):
        self.payloads = []
        self.per_query = per_query
        self.with_site_every = with_site_every
        self.page_token = page_token
        self.empty = empty

    async def post(self, _url, headers, json):
        self.payloads.append(json)
        if self.empty:
            return FakeResponse({"places": []})

        query = json["textQuery"]
        places = []
        for index in range(1, self.per_query + 1):
            place = {
                "id": f"{query}-{index}",
                "displayName": {"text": f"{query} {index}"},
                "internationalPhoneNumber": "+55 48 3025-6255",
            }
            if self.with_site_every and index % self.with_site_every == 0:
                place["websiteUri"] = "https://exemplo.com.br"
            places.append(place)

        payload = {"places": places}
        if self.page_token:
            payload["nextPageToken"] = self.page_token
        return FakeResponse(payload)


class FakeDb:
    def query(self, _column):
        return self

    def filter(self, _criterion):
        return self

    def all(self):
        return []


class SearchFieldMaskTests(unittest.TestCase):
    def test_mask_carries_the_fields_that_used_to_cost_a_details_call(self):
        # Os três campos entram no mesmo SKU Enterprise que `rating` já forçava, então
        # pedi-los na busca não muda o preço da chamada e dispensa o Place Details.
        for field in (
            "places.websiteUri",
            "places.internationalPhoneNumber",
            "places.googleMapsUri",
        ):
            self.assertIn(field, SEARCH_FIELD_MASK)


class PageSizeTests(unittest.TestCase):
    def test_every_page_asks_for_the_full_size(self):
        # A página é cobrada por chamada, não por resultado: pedir menos que 20 paga o
        # mesmo e colhe menos.
        client = FakeSearchClient()
        asyncio.run(
            _collect_batch(client, FakeDb(), resolve_search_plan("reformas"), {}, 3, 0, 0, 0)
        )

        self.assertTrue(client.payloads)
        self.assertTrue(all(p["maxResultCount"] == PAGE_SIZE for p in client.payloads))

    def test_first_page_of_the_wave_settles_the_batch_before_paginating(self):
        # Antes cada termo drenava as 3 páginas de uma vez, buscando até 300 lugares para
        # preencher 100 vagas. O excedente era descartado já pago.
        client = FakeSearchClient(per_query=PAGE_SIZE, page_token="proxima")
        collected, _, _, _, _ = asyncio.run(
            _collect_batch(client, FakeDb(), resolve_search_plan("reformas"), {}, PAGE_SIZE, 0, 0, 0)
        )

        self.assertEqual(len(collected), PAGE_SIZE)
        self.assertTrue(all("pageToken" not in p for p in client.payloads))


class WebsiteFilterTests(unittest.TestCase):
    def test_batch_fills_with_leads_that_survive_the_website_filter(self):
        # "Pedi 20 e vieram 20": o filtro roda antes de a linha ocupar vaga no lote.
        # Antes ele rodava depois do Details e encolhia o lote já pago.
        client = FakeSearchClient(per_query=4, with_site_every=2)
        collected, rejected, _, _, _ = asyncio.run(
            _collect_batch(
                client,
                FakeDb(),
                resolve_search_plan("reformas"),
                {},
                4,
                0,
                0,
                0,
                only_without_website=True,
            )
        )

        self.assertEqual(len(collected), 4)
        self.assertTrue(all(not place.get("websiteUri") for place, _ in collected))

    def test_rejected_leads_come_back_so_they_can_be_deduplicated(self):
        # Eles já foram pagos. Sem devolvê-los para o banco, a próxima busca na mesma
        # região paga por eles de novo.
        client = FakeSearchClient(per_query=4, with_site_every=2)
        _, rejected, _, _, _ = asyncio.run(
            _collect_batch(
                client,
                FakeDb(),
                resolve_search_plan("reformas"),
                {},
                4,
                0,
                0,
                0,
                only_without_website=True,
            )
        )

        self.assertTrue(rejected)
        self.assertTrue(all(place.get("websiteUri") for place, _ in rejected))


class BarrenWaveTests(unittest.TestCase):
    def test_batch_gives_up_once_waves_stop_producing(self):
        # Numa região esgotada o lote seguia pagando páginas até completar as 6 ondas.
        client = FakeSearchClient(empty=True)
        asyncio.run(
            _collect_batch(client, FakeDb(), resolve_search_plan("all"), {}, 100, 0, 0, 0)
        )

        waves_used = len({p["textQuery"] for p in client.payloads})
        self.assertLessEqual(waves_used, MAX_BARREN_WAVES * 5)


class PhoneFallbackTests(unittest.TestCase):
    def test_details_is_skipped_when_the_search_already_returned_a_phone(self):
        class ForbiddenClient:
            async def get(self, *_args, **_kwargs):
                raise AssertionError("Place Details não deveria ser chamado")

        query = resolve_search_plan("reformas")[0]
        collected = [({"id": "a", "internationalPhoneNumber": "+55 48 3025-6255"}, query)]
        asyncio.run(_fill_missing_phones(ForbiddenClient(), collected))

    def test_details_fills_only_the_places_that_came_without_a_phone(self):
        calls = []

        class CountingClient:
            async def get(self, url, headers):
                calls.append(url)
                return FakeResponse({"internationalPhoneNumber": "+55 48 99999-0000"})

        query = resolve_search_plan("reformas")[0]
        with_phone = {"id": "a", "internationalPhoneNumber": "+55 48 3025-6255"}
        without_phone = {"id": "b"}
        asyncio.run(_fill_missing_phones(CountingClient(), [(with_phone, query), (without_phone, query)]))

        self.assertEqual(len(calls), 1)
        self.assertEqual(without_phone["internationalPhoneNumber"], "+55 48 99999-0000")


if __name__ == "__main__":
    unittest.main()
