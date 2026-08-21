from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services.geocoding import get_coordinates


def _mock_client(payload: dict) -> MagicMock:
    response = MagicMock()
    response.json.return_value = payload
    client = AsyncMock()
    client.get = AsyncMock(return_value=response)
    client.__aenter__.return_value = client
    client.__aexit__.return_value = None
    return client


@pytest.mark.asyncio
async def test_get_coordinates_returns_lat_lng_on_ok():
    client = _mock_client(
        {
            "status": "OK",
            "results": [{"geometry": {"location": {"lat": -27.59, "lng": -48.55}}}],
        }
    )
    with patch("services.geocoding.httpx.AsyncClient", return_value=client):
        coords = await get_coordinates("Florianópolis", "")

    assert coords == {"lat": -27.59, "lng": -48.55}
    params = client.get.await_args.kwargs["params"]
    assert params["address"] == "Florianópolis, Brasil"


@pytest.mark.asyncio
async def test_get_coordinates_uses_place_id_when_provided():
    client = _mock_client(
        {
            "status": "OK",
            "results": [{"geometry": {"location": {"lat": -27.6, "lng": -48.5}}}],
        }
    )
    with patch("services.geocoding.httpx.AsyncClient", return_value=client):
        await get_coordinates("Florianópolis", "Centro", "ChIJplace")

    params = client.get.await_args.kwargs["params"]
    assert params["place_id"] == "ChIJplace"
    assert "address" not in params


@pytest.mark.asyncio
async def test_get_coordinates_uses_neighborhood_address():
    client = _mock_client(
        {
            "status": "OK",
            "results": [{"geometry": {"location": {"lat": -27.6, "lng": -48.5}}}],
        }
    )
    with patch("services.geocoding.httpx.AsyncClient", return_value=client):
        await get_coordinates("Florianópolis", "Centro")

    params = client.get.await_args.kwargs["params"]
    assert params["address"] == "Centro, Florianópolis, Brasil"


@pytest.mark.asyncio
async def test_get_coordinates_raises_on_api_error():
    client = _mock_client({"status": "ZERO_RESULTS", "results": []})
    with patch("services.geocoding.httpx.AsyncClient", return_value=client):
        with pytest.raises(ValueError, match="ZERO_RESULTS"):
            await get_coordinates("Cidade Inexistente", "")
