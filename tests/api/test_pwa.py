import json


def test_service_worker_is_served_with_js_content_type(client):
    response = client.get("/sw.js")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/javascript")
    assert "prospector" in response.text.lower()


def test_manifest_is_served_with_manifest_content_type(client):
    response = client.get("/manifest.webmanifest")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/manifest+json")

    manifest = json.loads(response.text)
    assert manifest["start_url"] == "/"
    assert manifest["display"] == "standalone"
    icon_sizes = {icon["sizes"] for icon in manifest["icons"]}
    assert "192x192" in icon_sizes
    assert "512x512" in icon_sizes


def test_offline_page_renders_without_a_session(client):
    response = client.get("/offline")
    assert response.status_code == 200
    assert "sem conexão" in response.text.lower()
