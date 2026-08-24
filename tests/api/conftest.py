import pytest
from fastapi.testclient import TestClient

from database.connection import SessionLocal, engine, get_db
from database.models import AppUser, Base, Business
from main import app
from services.auth import get_current_user
from services.deduplication import existing_place_ids


@pytest.fixture
def db_session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: AppUser(
        clerk_user_id="user_test_admin",
        role="admin",
        is_active=True,
    )
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def mock_google(monkeypatch):
    async def fake_coordinates(*_args, **_kwargs):
        return {"lat": -27.59, "lng": -48.55}

    async def fake_collect_batch(_client, db, plan, *_args, **_kwargs):
        place = {
            "id": "place-1",
            "displayName": {"text": "Padaria Teste"},
            "formattedAddress": "Rua das Flores, 10",
        }
        if existing_place_ids(db, [place["id"]]):
            return [], 1, 1, None
        return [(place, plan[0])], 1, 0, None

    async def fake_details(_client, _place_id):
        return {
            "internationalPhoneNumber": "+55 48 3025-6255",
            "websiteUri": None,
            "googleMapsUri": "https://maps.google.com/?cid=1",
        }

    monkeypatch.setattr("services.places.get_coordinates", fake_coordinates)
    monkeypatch.setattr("services.places._collect_batch", fake_collect_batch)
    monkeypatch.setattr("services.places._fetch_details", fake_details)


@pytest.fixture
def seeded_businesses(db_session):
    with_site = Business(
        place_id="place-site",
        name="Loja Com Site",
        address="Rua A",
        phone="+55 48 98471-4240",
        maps_url="https://maps.google.com/?cid=2",
        has_website=True,
        business_type="clothing_store",
    )
    without_site = Business(
        place_id="place-no-site",
        name="Padaria Sem Site",
        address="Rua B",
        phone="+55 48 3025-6255",
        maps_url="https://maps.google.com/?cid=3",
        has_website=False,
        business_type="bakery",
    )
    db_session.add_all([with_site, without_site])
    db_session.commit()
    db_session.refresh(with_site)
    db_session.refresh(without_site)
    return with_site, without_site
