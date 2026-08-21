def test_history_lists_seeded_leads(client, seeded_businesses):
    response = client.get("/historico")
    assert response.status_code == 200
    html = response.text
    assert "Loja Com Site" in html
    assert "Padaria Sem Site" in html


def test_history_filters_by_name(client, seeded_businesses):
    response = client.get("/historico", params={"name": "Padaria"})
    assert response.status_code == 200
    assert "Padaria Sem Site" in response.text
    assert "Loja Com Site" not in response.text


def test_history_filters_by_has_website(client, seeded_businesses):
    response = client.get("/historico", params={"has_website": "false"})
    assert response.status_code == 200
    assert "Padaria Sem Site" in response.text
    assert "Loja Com Site" not in response.text


def test_history_whatsapp_link_inserts_ninth_digit(client, seeded_businesses):
    response = client.get("/historico")
    assert "https://wa.me/5548930256255" in response.text
    assert "https://wa.me/5548984714240" in response.text


def test_delete_history_removes_selected_ids(client, db_session, seeded_businesses):
    with_site, without_site = seeded_businesses
    response = client.request("DELETE", "/historico", json={"ids": [without_site.id]})
    assert response.status_code == 200
    assert response.json()["deleted"] == 1

    remaining = client.get("/historico")
    assert "Padaria Sem Site" not in remaining.text
    assert "Loja Com Site" in remaining.text


def test_delete_history_rejects_empty_ids(client):
    response = client.request("DELETE", "/historico", json={"ids": []})
    assert response.status_code == 400
