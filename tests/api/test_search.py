from database.models import Business

SEARCH_PAYLOAD = {
    "city": "Florianópolis",
    "neighborhood": "Centro",
    "business_type": "bakery",
    "quantity": 5,
    "only_without_website": False,
}


def test_search_saves_new_lead(client, db_session, mock_google):
    response = client.post("/search", json=SEARCH_PAYLOAD)
    assert response.status_code == 200
    body = response.json()
    assert body["summary"]["new_saved"] == 1
    assert body["summary"]["skipped_duplicates"] == 0
    assert body["results"][0]["name"] == "Padaria Teste"
    assert body["results"][0]["phone"] == "+55 48 3025-6255"


def test_search_skips_duplicate_place_id(client, db_session, mock_google):
    first = client.post("/search", json=SEARCH_PAYLOAD)
    assert first.status_code == 200
    second = client.post("/search", json=SEARCH_PAYLOAD)
    assert second.status_code == 200
    assert second.json()["summary"]["skipped_duplicates"] == 1
    assert second.json()["summary"]["new_saved"] == 0


def test_search_rejects_invalid_business_type(client, mock_google):
    payload = {**SEARCH_PAYLOAD, "business_type": "tipo_inexistente"}
    response = client.post("/search", json=payload)
    assert response.status_code == 400
    assert "inválido" in response.json()["detail"]


def test_search_accepts_the_all_business_type(client, db_session, mock_google):
    payload = {**SEARCH_PAYLOAD, "business_type": "all"}
    response = client.post("/search", json=payload)
    assert response.status_code == 200
    assert response.json()["summary"]["new_saved"] == 1

    # Mesmo no modo "todos", o lead guarda a categoria real que o encontrou.
    saved = db_session.query(Business).one()
    assert saved.business_type != "all"


def test_search_response_carries_the_batch_cursor(client, mock_google):
    response = client.post("/search", json={**SEARCH_PAYLOAD, "quantity": 1000})
    assert response.status_code == 200
    assert response.json()["cursor"] is None


def test_search_rejects_quantity_above_the_ceiling(client, mock_google):
    response = client.post("/search", json={**SEARCH_PAYLOAD, "quantity": 1001})
    assert response.status_code == 422
