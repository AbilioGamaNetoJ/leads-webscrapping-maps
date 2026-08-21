import asyncio
import unittest

from database.models import Business
from services.business_type_catalog import NICHE_CATALOG
from services.business_types import as_dicts, get_business_type
from services.places import _fetch_category_places, build_search_body


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
        class FakeResponse:
            def __init__(self, payload):
                self.payload = payload
                self.status_code = 200

            def json(self):
                return self.payload

        class FakeClient:
            def __init__(self):
                self.payloads = []

            async def post(self, _, headers, json):
                self.payloads.append(json)
                query = json["textQuery"]
                return FakeResponse(
                    {
                        "places": [
                            {"id": f"{query}-1"},
                            {"id": f"{query}-2"},
                        ]
                    }
                )

        client = FakeClient()
        category = get_business_type("caca_vazamento")
        places, total_checked = asyncio.run(
            _fetch_category_places(client, category, {"low": {}, "high": {}}, 5)
        )

        self.assertEqual(len(places), 5)
        self.assertEqual(total_checked, 6)
        self.assertEqual({payload["textQuery"] for payload in client.payloads}, set(category.search_terms))
        self.assertTrue(all("includedType" not in payload for payload in client.payloads))

    def test_business_type_is_persistable(self):
        self.assertIn("business_type", Business.__table__.columns)


if __name__ == "__main__":
    unittest.main()
