from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from database.models import Business
from routers.search import SearchRequest
from services.deduplication import existing_place_ids
from services.places import _circle_to_rectangle, build_search_body, search_businesses
from services.business_types import get_business_type


def test_circle_to_rectangle_has_low_and_high():
    rectangle = _circle_to_rectangle(-27.59, -48.55, 2000.0)
    assert rectangle["low"]["latitude"] < -27.59
    assert rectangle["high"]["latitude"] > -27.59
    assert rectangle["low"]["longitude"] < -48.55
    assert rectangle["high"]["longitude"] > -48.55


def test_build_search_body_without_included_type():
    body = build_search_body("caça vazamento", {"low": {}, "high": {}}, 5)
    assert body["textQuery"] == "caça vazamento"
    assert body["maxResultCount"] == 5
    assert "includedType" not in body
    assert "strictTypeFiltering" not in body


def test_build_search_body_with_official_type():
    category = get_business_type("restaurant")
    body = build_search_body("restaurante", {"low": {}, "high": {}}, 10, category.included_type)
    assert body["includedType"] == "restaurant"
    assert body["strictTypeFiltering"] is True


def test_build_search_body_includes_page_token():
    body = build_search_body("padaria", {"low": {}, "high": {}}, 5, page_token="abc")
    assert body["pageToken"] == "abc"


def _base_request(**overrides):
    payload = {"city": "Florianópolis", "business_type": "all", "quantity": 20}
    payload.update(overrides)
    return SearchRequest(**payload)


def test_search_request_accepts_the_new_ceiling():
    assert _base_request(quantity=1000).quantity == 1000


def test_search_request_rejects_above_the_ceiling():
    with pytest.raises(ValidationError):
        _base_request(quantity=1001)


def test_search_request_defaults_to_the_first_batch():
    request = _base_request()
    assert request.cursor == 0
    assert request.batch_size == 100


def test_existing_place_ids_returns_only_known_ids(db_session):
    db_session.add(
        Business(
            place_id="place-known",
            name="Padaria",
            address="Rua A",
            phone="+55 48 3025-6255",
            maps_url="",
            has_website=False,
        )
    )
    db_session.commit()

    found = existing_place_ids(db_session, ["place-known", "place-new", "place-known"])
    assert found == {"place-known"}


def test_existing_place_ids_skips_the_database_when_empty(db_session):
    assert existing_place_ids(db_session, []) == set()


@pytest.mark.asyncio
async def test_search_businesses_rejects_invalid_category():
    with pytest.raises(ValueError, match="inválido"):
        await search_businesses(
            db=MagicMock(),
            city="Florianópolis",
            neighborhood="",
            business_type="tipo_inexistente",
            quantity=5,
            only_without_website=False,
        )
