from unittest.mock import MagicMock

import pytest

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
