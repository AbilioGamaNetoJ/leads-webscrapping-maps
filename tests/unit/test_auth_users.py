import asyncio
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from database.models import AppUser
from routers import auth as auth_router
from routers import webhooks
from routers.webhooks import _primary_email
from services.auth import (
    LoginRequired,
    get_current_user,
    is_safe_return_to,
    require_admin,
    require_same_origin,
)
from services.clerk import _required_setting, list_pending_invitations
from services.users import deactivate_user, get_user, set_user_active, upsert_user


def test_safe_return_to_allows_only_internal_paths():
    assert is_safe_return_to("/historico?page=2") == "/historico?page=2"
    assert is_safe_return_to("https://example.com") == "/"
    assert is_safe_return_to("//example.com") == "/"


def test_jwt_setting_normalizes_escaped_newlines(monkeypatch):
    monkeypatch.setenv("CLERK_JWT_KEY", "-----BEGIN PUBLIC KEY-----\\nkey\\n-----END PUBLIC KEY-----")

    assert _required_setting("CLERK_JWT_KEY") == "-----BEGIN PUBLIC KEY-----\nkey\n-----END PUBLIC KEY-----"


def test_pending_invitations_accepts_clerk_list_response(monkeypatch):
    monkeypatch.setattr(
        "services.clerk._backend_request",
        lambda *_args, **_kwargs: [{"id": "inv_1"}],
    )

    assert list_pending_invitations() == [{"id": "inv_1"}]


def test_pending_invitations_accepts_enveloped_response(monkeypatch):
    monkeypatch.setattr(
        "services.clerk._backend_request",
        lambda *_args, **_kwargs: {"data": [{"id": "inv_2"}]},
    )

    assert list_pending_invitations() == [{"id": "inv_2"}]


def test_upsert_user_assigns_configured_admin(db_session):
    user = upsert_user(
        db_session,
        "user_admin",
        admin_user_id="user_admin",
        email="admin@example.com",
        first_name="Admin",
    )

    assert user.role == "admin"
    assert user.is_active is True
    assert user.full_name == "Admin"


def test_deactivate_and_reactivate_user(db_session):
    upsert_user(db_session, "user_member", email="member@example.com")

    deactivated = deactivate_user(db_session, "user_member")
    assert deactivated is not None
    assert deactivated.is_active is False
    assert deactivated.deleted_at is not None

    reactivated = set_user_active(db_session, "user_member", True)
    assert reactivated is not None
    assert reactivated.is_active is True
    assert reactivated.deleted_at is None
    assert get_user(db_session, "user_member") is not None


def test_primary_email_uses_clerk_primary_address():
    payload = {
        "primary_email_address_id": "email_primary",
        "email_addresses": [
            {"id": "email_other", "email_address": "other@example.com"},
            {"id": "email_primary", "email_address": "primary@example.com"},
        ],
    }

    assert _primary_email(payload) == "primary@example.com"


def test_anonymous_requests_redirect_pages_and_reject_apis():
    page_request = SimpleNamespace(session={}, url=SimpleNamespace(path="/historico"))
    with pytest.raises(LoginRequired) as error:
        get_current_user(page_request, SimpleNamespace())
    assert error.value.return_to == "/historico"

    api_request = SimpleNamespace(session={}, url=SimpleNamespace(path="/search"))
    with pytest.raises(HTTPException) as error:
        get_current_user(api_request, SimpleNamespace())
    assert error.value.status_code == 401


def test_session_exchange_accepts_valid_token_and_rejects_invalid(monkeypatch, db_session):
    monkeypatch.setattr(auth_router, "verify_session_token", lambda _request: {"sub": "user_member"})
    monkeypatch.setattr(auth_router, "get_user_profile", lambda _user_id: {})
    monkeypatch.setenv("CLERK_ADMIN_USER_ID", "user_admin")
    request = SimpleNamespace(session={})

    response = auth_router.create_session(request, None, db_session)

    assert response.status_code == 204
    assert request.session == {"clerk_user_id": "user_member"}

    monkeypatch.setattr(auth_router, "verify_session_token", lambda _request: None)
    with pytest.raises(HTTPException) as error:
        auth_router.create_session(SimpleNamespace(session={}), None, db_session)
    assert error.value.status_code == 401


def test_session_exchange_syncs_clerk_profile(monkeypatch, db_session):
    monkeypatch.setattr(auth_router, "verify_session_token", lambda _request: {"sub": "user_profile"})
    monkeypatch.setattr(
        auth_router,
        "get_user_profile",
        lambda _user_id: {
            "email": "profile@example.com",
            "first_name": "Maria",
            "last_name": "Silva",
            "image_url": "https://img.example.com/profile.png",
        },
    )
    monkeypatch.setenv("CLERK_ADMIN_USER_ID", "user_admin")

    auth_router.create_session(SimpleNamespace(session={}), None, db_session)

    user = db_session.get(AppUser, "user_profile")
    assert user.email == "profile@example.com"
    assert user.full_name == "Maria Silva"
    assert user.image_url == "https://img.example.com/profile.png"


def test_session_exchange_rejects_inactive_user(monkeypatch, db_session):
    upsert_user(db_session, "user_member", email="member@example.com")
    deactivate_user(db_session, "user_member")
    monkeypatch.setattr(auth_router, "verify_session_token", lambda _request: {"sub": "user_member"})

    with pytest.raises(HTTPException) as error:
        auth_router.create_session(SimpleNamespace(session={}), None, db_session)

    assert error.value.status_code == 403


def test_admin_and_origin_guards(monkeypatch):
    member = SimpleNamespace(role="member")
    with pytest.raises(HTTPException) as error:
        require_admin(member)
    assert error.value.status_code == 403

    monkeypatch.setenv("APP_URL", "http://testserver")
    valid_request = Request(
        {
            "type": "http",
            "method": "POST",
            "scheme": "http",
            "path": "/search",
            "headers": [(b"origin", b"http://testserver")],
            "server": ("testserver", 80),
        }
    )
    require_same_origin(valid_request)

    invalid_request = Request(
        {
            "type": "http",
            "method": "POST",
            "scheme": "http",
            "path": "/search",
            "headers": [(b"origin", b"https://example.com")],
            "server": ("testserver", 80),
        }
    )
    with pytest.raises(HTTPException) as error:
        require_same_origin(invalid_request)
    assert error.value.status_code == 403


def test_user_webhook_is_idempotent_and_invalid_signature_is_rejected(monkeypatch, db_session):
    event = {
        "type": "user.created",
        "data": {
            "id": "user_webhook",
            "primary_email_address_id": "email_1",
            "email_addresses": [{"id": "email_1", "email_address": "webhook@example.com"}],
            "first_name": "Webhook",
            "last_name": "User",
        },
    }
    monkeypatch.setattr(webhooks, "_verify_event", lambda _body, _headers: event)
    request = SimpleNamespace(headers={}, body=lambda: None)

    async def body():
        return b"{}"

    request.body = body
    asyncio.run(webhooks.clerk_webhook(request, db_session))
    asyncio.run(webhooks.clerk_webhook(request, db_session))

    users = db_session.query(AppUser).all()
    assert len(users) == 1
    assert users[0].email == "webhook@example.com"

    monkeypatch.setattr(webhooks, "_verify_event", lambda _body, _headers: (_ for _ in ()).throw(ValueError()))
    with pytest.raises(HTTPException) as error:
        asyncio.run(webhooks.clerk_webhook(request, db_session))
    assert error.value.status_code == 400
