import os
from collections.abc import Mapping
from typing import Any
from urllib.parse import quote

import httpx

CLERK_API_URL = "https://api.clerk.com/v1"


class ClerkConfigurationError(RuntimeError):
    pass


class ClerkApiError(RuntimeError):
    pass


def _required_setting(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ClerkConfigurationError(f"A variável {name} não está configurada.")
    if name == "CLERK_JWT_KEY":
        value = value.strip().replace("\\n", "\n")
    return value


def verify_session_token(request: Any) -> Mapping[str, Any] | None:
    try:
        from clerk_backend_api import AuthenticateRequestOptions, authenticate_request
    except ImportError as error:
        raise ClerkConfigurationError("A dependência clerk-backend-api não está instalada.") from error

    state = authenticate_request(
        request,
        AuthenticateRequestOptions(
            secret_key=_required_setting("CLERK_SECRET_KEY"),
            jwt_key=_required_setting("CLERK_JWT_KEY"),
            authorized_parties=[_required_setting("APP_URL")],
            accepts_token=["session_token"],
        ),
    )
    if not state.is_signed_in:
        return None
    return dict(state.payload)


def create_invitation(email: str, redirect_url: str) -> dict[str, Any]:
    return _backend_request(
        "POST",
        "/invitations",
        json={"email_address": email, "redirect_url": redirect_url},
    )


def get_user_profile(user_id: str) -> dict[str, str | None]:
    """Fetch the Clerk profile needed to display a local app user."""
    payload = _backend_request("GET", f"/users/{quote(user_id, safe='')}")
    if not isinstance(payload, Mapping):
        return {}

    primary_email_id = payload.get("primary_email_address_id")
    email = next(
        (
            item.get("email_address")
            for item in payload.get("email_addresses", [])
            if isinstance(item, Mapping) and item.get("id") == primary_email_id
        ),
        None,
    )
    return {
        "email": email,
        "first_name": payload.get("first_name"),
        "last_name": payload.get("last_name"),
        "image_url": payload.get("image_url"),
    }


def list_pending_invitations() -> list[dict[str, Any]]:
    response = _backend_request("GET", "/invitations", params={"status": "pending"})
    if isinstance(response, list):
        return [invitation for invitation in response if isinstance(invitation, dict)]
    if isinstance(response, Mapping):
        data = response.get("data", [])
        if isinstance(data, list):
            return [invitation for invitation in data if isinstance(invitation, dict)]
    return []


def revoke_invitation(invitation_id: str) -> dict[str, Any]:
    return _backend_request("POST", f"/invitations/{invitation_id}/revoke")


def _backend_request(
    method: str,
    path: str,
    *,
    json: dict[str, Any] | None = None,
    params: dict[str, str] | None = None,
) -> Any:
    try:
        response = httpx.request(
            method,
            f"{CLERK_API_URL}{path}",
            headers={"Authorization": f"Bearer {_required_setting('CLERK_SECRET_KEY')}"},
            json=json,
            params=params,
            timeout=15.0,
        )
        response.raise_for_status()
    except httpx.HTTPError as error:
        raise ClerkApiError("Não foi possível concluir a operação no Clerk.") from error
    return response.json()
