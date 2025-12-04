# backend/services/goto_service.py

from __future__ import annotations

import asyncio
import logging
import os
import time
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------------------
# Environment / Config
# --------------------------------------------------------------------------------------

GOTO_AUTH_BASE = os.getenv("GOTO_AUTH_BASE", "https://authentication.logmeininc.com")
GOTO_TOKEN_URL = os.getenv(
    "GOTO_TOKEN_URL", f"{GOTO_AUTH_BASE}/oauth/token"
)

GOTO_API_BASE = os.getenv("GOTO_API_BASE", "https://api.goto.com")

GOTO_CLIENT_ID = os.getenv("GOTO_CLIENT_ID")
GOTO_CLIENT_SECRET = os.getenv("GOTO_CLIENT_SECRET")

GOTO_REDIRECT_URI = os.getenv("GOTO_REDIRECT_URI", "https://localhost/goto")

GOTO_SCOPES = os.getenv(
    "GOTO_SCOPES",
    "messaging.v1.send messaging.v1.read webrtc.v1.write call-events.v1.notifications.manage call-events.v1.events.read",
)

GOTO_REFRESH_TOKEN = os.getenv("GOTO_REFRESH_TOKEN")

if not GOTO_CLIENT_ID or not GOTO_CLIENT_SECRET:
    logger.warning("GoTo OAuth client ID/secret not fully configured in env vars.")

if not GOTO_REFRESH_TOKEN:
    logger.warning(
        "GOTO_REFRESH_TOKEN is not set. You must obtain a refresh token via the "
        "Authorization Code flow and set it as an env var."
    )

# --------------------------------------------------------------------------------------
# Internal token cache
# --------------------------------------------------------------------------------------

_token_cache: Dict[str, Any] | None = None
_token_lock = asyncio.Lock()


class GoToError(Exception):
    """Custom exception type for GoTo API errors."""


# --------------------------------------------------------------------------------------
# Low-level HTTP helpers
# --------------------------------------------------------------------------------------


def _build_basic_auth_header(client_id: str, client_secret: str) -> Dict[str, str]:
    """Return HTTP Basic Authorization header for client_id:client_secret."""
    import base64

    pair = f"{client_id}:{client_secret}"
    token = base64.b64encode(pair.encode("utf-8")).decode("ascii")
    return {"Authorization": f"Basic {token}"}


async def _refresh_access_token() -> str:
    """
    Refresh an access token using the stored refresh token.
    """
    global _token_cache

    if not (GOTO_CLIENT_ID and GOTO_CLIENT_SECRET and GOTO_REFRESH_TOKEN):
        raise GoToError(
            "GoTo OAuth env vars not fully configured "
            "(GOTO_CLIENT_ID, GOTO_CLIENT_SECRET, GOTO_REFRESH_TOKEN)."
        )

    data = {
        "grant_type": "refresh_token",
        "refresh_token": GOTO_REFRESH_TOKEN,
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        **_build_basic_auth_header(GOTO_CLIENT_ID, GOTO_CLIENT_SECRET),
    }

    logger.info("Requesting new GoTo access token via refresh_token")

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(GOTO_TOKEN_URL, data=data, headers=headers)

    if resp.status_code != 200:
        logger.error(
            "GoTo token refresh failed: status=%s body=%s",
            resp.status_code,
            resp.text,
        )
        raise GoToError(
            f"GoTo token refresh failed with status {resp.status_code}: {resp.text}"
        )

    token_data = resp.json()
    access_token = token_data.get("access_token")
    if not access_token:
        logger.error("GoTo token refresh response missing access_token: %s", token_data)
        raise GoToError("GoTo token refresh response missing access_token")

    expires_in = token_data.get("expires_in", 300)  # seconds

    _token_cache = {
        "access_token": access_token,
        "expires_at": time.time() + expires_in - 30,
    }

    logger.info("GoTo access token refreshed successfully (expires_in=%s)", expires_in)
    return access_token


async def _cached_token() -> str:
    """
    Return a valid access token, using in-memory cache + refresh if needed.
    """
    global _token_cache

    async with _token_lock:
        if _token_cache and _token_cache.get("expires_at", 0) > time.time():
            return _token_cache["access_token"]

        return await _refresh_access_token()


# --------------------------------------------------------------------------------------
# Public helper: send SMS
# --------------------------------------------------------------------------------------


async def send_sms(
    owner_phone_number: str,
    contact_phone_numbers: List[str],
    body: str,
    user_key: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Send an SMS message using the GoTo Messaging API.
    """

    if not contact_phone_numbers:
        raise ValueError("contact_phone_numbers must contain at least one number")

    token = await _cached_token()

    url = f"{GOTO_API_BASE}/messaging/v1/messages"
    payload: Dict[str, Any] = {
        "ownerPhoneNumber": owner_phone_number,
        "contactPhoneNumbers": contact_phone_numbers,
        "body": body,
    }
    if user_key:
        payload["userKey"] = user_key

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    logger.info(
        "Sending GoTo SMS: owner=%s contacts=%s len(body)=%d",
        owner_phone_number,
        contact_phone_numbers,
        len(body),
    )
    logger.debug("GoTo SMS payload=%s", payload)

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(url, json=payload, headers=headers)

    if resp.status_code not in (200, 201):
        logger.error(
            "GoTo SMS send failed: status=%s body=%s",
            resp.status_code,
            resp.text,
        )
        raise GoToError(
            f"GoTo SMS send failed with status {resp.status_code}: {resp.text}"
        )

    data = resp.json()
    logger.info("GoTo SMS sent successfully, response id=%s", data.get("id"))
    logger.debug("GoTo SMS response full body=%s", data)
    return data


# --------------------------------------------------------------------------------------
# Public helper: start call (stub)
# --------------------------------------------------------------------------------------


async def start_call(
    from_extension: str,
    to_number: str,
    device_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Placeholder for GoTo call control integration.
    """
    logger.warning(
        "start_call() invoked but not implemented. "
        "from_extension=%s to_number=%s device_id=%s metadata=%s",
        from_extension,
        to_number,
        device_id,
        metadata,
    )
    raise GoToError(
        "start_call() is not implemented yet. Wire this to GoTo Devices & Calls API."
    )


# --------------------------------------------------------------------------------------
# Optional: debug helper
# --------------------------------------------------------------------------------------


async def debug_get_raw_access_token() -> str:
    """Return the current cached access token (for local debugging only)."""
    return await _cached_token()


# --------------------------------------------------------------------------------------
# Legacy-style service object (to match `from services.goto_service import goto_service`)
# --------------------------------------------------------------------------------------


class GoToService:
    async def send_sms(
        self,
        owner_phone_number: str,
        contact_phone_numbers: List[str],
        body: str,
        user_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        return await send_sms(owner_phone_number, contact_phone_numbers, body, user_key)

    async def start_call(
        self,
        from_extension: str,
        to_number: str,
        device_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return await start_call(from_extension, to_number, device_id, metadata)


# This is what your existing sms_routes.py is importing
goto_service = GoToService()
