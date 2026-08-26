import asyncio
import unittest

from database.models import Business
from services.business_type_catalog import NICHE_CATALOG
from services.business_types import (
    ALL_BUSINESS_TYPES_VALUE,
    as_dicts,
    get_business_type,
    resolve_search_plan,
)
from services.places import _collect_batch, build_search_body


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload
        self.status_code = 200

    def json(self):
        return self.payload


class FakeClient:
    """Devolve dois lugares por termo, sem paginação."""

    def __init__(self, rating=None, reviews=None):
        self.payloads = []
        self.rating = rating
        self.reviews = reviews

    async def post(self, _, headers, json):
        self.payloads.append(json)
        query = json["textQuery"]
        places = []
        for index in (1, 2):
            place = {"id": f"{query}-{index}"}
            if self.rating is not None:
                place["rating"] = self.rating
            if self.reviews is not None:
                place["userRatingCount"] = self.reviews
            places.append(place)
        return FakeResponse({"places": places})


class FakeDb:
    """Substitui a sessão só para o `existing_place_ids` do laço de coleta."""

    def __init__(self, known=None):
        self.known = set(known or ())

    def query(self, _column):
        return self

    def filter(self, _criterion):
        return self

    def all(self):
        # Devolver ids fora do bloco consultado é inofensivo: quem chama testa pertinência.
        return [(place_id,) for place_id in self.known]


class BusinessTypeCatalogTests(unittest.TestCase):
    def test_all_commercial_niches_are_present_with_queries(self):
        self.assertEqual(len(NICHE_CATALOG), 92)
        self.assertEqual(sum(len(queries) for _, _, queries, _ in NICHE_CATALOG), 387)
        self.assertEqual(len({value for value, _, _, _ in NICHE_CATALOG}), 92)
        self.assertTrue(all(queries for _, _, queries, _ in NICHE_CATALOG))

    def test_representative_niches_preserve_all_requested_terms(self):
        catalog = {value: queries for value, _, queries, _ in NICHE_CATALOG}
        self.assertIn("Oficina de conserto de móveis", catalog["moveis_planejados_marcenaria"])
        self.assertIn("Serviço de detecção de vazamentos", catalog["caca_vazamento"])
        self.assertIn("Advogado previdenciário", catalog["advocacia"])
        self.assertIn("Hospital veterinário", catalog["veterinary_care"])
        self.assertIn("Serviço de restauração de móveis", catalog["tapecaria_reforma_de_estofados"])

    def test_categories_are_available_to_the_combobox(self):
        options = {item["value"]: item for item in as_dicts()}
        for value, _, queries, _ in NICHE_CATALOG:
            self.assertIn(value, options)
            self.assertTrue(set(queries).issubset(options[value]["aliases"]))

    def test_only_official_types_use_the_places_filter(self):
        custom_category = get_business_type("caca_vazamento")
        official_category = get_business_type("restaurant")
        self.assertIsNotNone(custom_category)
        self.assertIsNotNone(official_category)

        rectangle = {"low": {}, "high": {}}
        custom_body = build_search_body(
            custom_category.search_terms[0],
            rectangle,
            5,
            custom_category.included_type,
        )
        official_body = build_search_body(
            official_category.search_terms[0],
            rectangle,
            5,
            official_category.included_type,
        )

        self.assertNotIn("includedType", custom_body)
        self.assertNotIn("strictTypeFiltering", custom_body)
        self.assertEqual(official_body["includedType"], "restaurant")
        self.assertTrue(official_body["strictTypeFiltering"])

    def test_composite_category_distributes_text_queries_without_type_filter(self):
        client = FakeClient()
        category = get_business_type("caca_vazamento")
        plan = resolve_search_plan("caca_vazamento")
        # batch_size alto o bastante para o lote percorrer o plano inteiro.
        collected, _, total_checked, skipped, next_cursor = asyncio.run(
            _collect_batch(client, FakeDb(), plan, {"low": {}, "high": {}}, 200, 0, 0, 0)
        )

        self.assertEqual(len(collected), 2 * len(category.search_terms))
        self.assertEqual(total_checked, len(collected))
        self.assertEqual(skipped, 0)
        self.assertIsNone(next_cursor)
        self.assertEqual({payload["textQuery"] for payload in client.payloads}, set(category.search_terms))
        self.assertTrue(all("includedType" not in payload for payload in client.payloads))

    def test_business_type_is_persistable(self):
        self.assertIn("business_type", Business.__table__.columns)


class SearchPlanTests(unittest.TestCase):
    def test_single_category_plan_preserves_its_search_terms(self):
        plan = resolve_search_plan("caca_vazamento")
        category = get_business_type("caca_vazamento")

        self.assertEqual([query.text for query in plan], list(category.search_terms))
        self.assertTrue(all(query.category_value == "caca_vazamento" for query in plan))

    def test_unknown_category_yields_an_empty_plan(self):
        self.assertEqual(resolve_search_plan("tipo_inexistente"), ())

    def test_all_plan_is_deterministic_and_free_of_duplicates(self):
        plan = resolve_search_plan(ALL_BUSINESS_TYPES_VALUE)

        self.assertEqual(plan, resolve_search_plan(ALL_BUSINESS_TYPES_VALUE))
        self.assertGreater(len(plan), len(resolve_search_plan("caca_vazamento")))

        keys = [(query.text, query.included_type) for query in plan]
        self.assertEqual(len(keys), len(set(keys)))

    def test_all_plan_interleaves_categories(self):
        plan = resolve_search_plan(ALL_BUSINESS_TYPES_VALUE)
        head = [query.category_value for query in plan[:10]]

        # O round-robin garante variedade logo nos primeiros termos consumidos.
        self.assertEqual(len(set(head)), len(head))

    def test_all_option_is_only_offered_when_requested(self):
        self.assertNotIn(ALL_BUSINESS_TYPES_VALUE, {item["value"] for item in as_dicts()})

        with_all = as_dicts(include_all=True)
        self.assertEqual(with_all[0]["value"], ALL_BUSINESS_TYPES_VALUE)
        self.assertEqual(len(with_all), len(as_dicts()) + 1)

    def test_all_is_not_a_real_category(self):
        self.assertIsNone(get_business_type(ALL_BUSINESS_TYPES_VALUE))


class BatchCursorTests(unittest.TestCase):
    def test_batches_advance_without_repeating_queries(self):
        plan = resolve_search_plan("reformas")
        rectangle = {"low": {}, "high": {}}

        first_client = FakeClient()
        first, _, _, _, cursor = asyncio.run(
            _collect_batch(first_client, FakeDb(), plan, rectangle, 2, 0, 0, 0)
        )
        self.assertEqual(len(first), 2)
        self.assertIsNotNone(cursor)
        self.assertGreater(cursor, 0)

        second_client = FakeClient()
        second, _, _, _, _ = asyncio.run(
            _collect_batch(second_client, FakeDb(), plan, rectangle, 2, cursor, 0, 0)
        )

        first_queries = {payload["textQuery"] for payload in first_client.payloads}
        second_queries = {payload["textQuery"] for payload in second_client.payloads}
        self.assertFalse(first_queries & second_queries)

        first_ids = {place["id"] for place, _ in first}
        second_ids = {place["id"] for place, _ in second}
        self.assertFalse(first_ids & second_ids)

    def test_exhausted_plan_reports_no_next_cursor(self):
        plan = resolve_search_plan("caca_vazamento")
        _, _, _, _, cursor = asyncio.run(
            _collect_batch(FakeClient(), FakeDb(), plan, {"low": {}, "high": {}}, 500, 0, 0, 0)
        )
        self.assertIsNone(cursor)

    def test_known_place_ids_are_counted_as_duplicates(self):
        plan = resolve_search_plan("caca_vazamento")
        db = FakeDb(known={f"{plan[0].text}-1"})
        collected, _, _, skipped, _ = asyncio.run(
            _collect_batch(FakeClient(), db, plan, {"low": {}, "high": {}}, 5, 0, 0, 0)
        )

        self.assertEqual(skipped, 1)
        self.assertNotIn(f"{plan[0].text}-1", {place["id"] for place, _ in collected})

    def test_rating_and_review_floors_are_applied_before_the_batch_cut(self):
        plan = resolve_search_plan("caca_vazamento")
        client = FakeClient(rating=3.0, reviews=5)
        collected, _, _, _, _ = asyncio.run(
            _collect_batch(client, FakeDb(), plan, {"low": {}, "high": {}}, 5, 0, 4.5, 0)
        )
        self.assertEqual(collected, [])


if __name__ == "__main__":
    unittest.main()
