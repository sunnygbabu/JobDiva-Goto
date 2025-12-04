# app/backend/services/jobdiva_service.py
"""
Async JobDiva helper service.

Provides:
- async create_candidate_note(candidate_id, note_text, recruiter_id=None)
- async find_candidate_by_phone(phone_e164)
"""

import os
import httpx
import asyncio
from typing import Optional


JOBDIVA_BASE_URL = os.getenv("JOBDIVA_BASE_URL", "https://api.jobdiva.com")

# Use ENV VAR NAMES here, not literal values
JOBDIVA_CLIENT_ID = os.getenv("JOBDIVA_CLIENT_ID")   # optional based on JobDiva auth
JOBDIVA_USERNAME = os.getenv("JOBDIVA_USERNAME")
JOBDIVA_PASSWORD = os.getenv("JOBDIVA_PASSWORD")
JOBDIVA_API_KEY = os.getenv("JOBDIVA_API_KEY")  # if JobDiva uses API key

# If JobDiva uses a token-based auth, cache token here
_jd_token_cache = {"token": None, "expires_at": 0}
_jd_lock = asyncio.Lock()


async def _get_jobdiva_headers() -> dict:
    """
    Return headers required by JobDiva API.
    Adjust based on the actual auth method JobDiva expects:
    - API key in header
    - or Basic/Auth token via a login endpoint
    """
    # If they provide an API key:
    if JOBDIVA_API_KEY:
        return {"Content-Type": "application/json", "Authorization": f"Bearer {JOBDIVA_API_KEY}"}

    # Otherwise, implement a login -> get token flow (placeholder)
    async with _jd_lock:
        import time

        now = time.time()
        if _jd_token_cache["token"] and now < _jd_token_cache["expires_at"] - 30:
            return {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {_jd_token_cache['token']}",
            }

        if JOBDIVA_USERNAME and JOBDIVA_PASSWORD:
            # TODO: replace /auth/login with the actual JobDiva auth endpoint
            login_url = f"{JOBDIVA_BASE_URL}/auth/login"
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(
                    login_url,
                    json={
                        "username": JOBDIVA_USERNAME,
                        "password": JOBDIVA_PASSWORD,
                        # include client_id if JobDiva requires it
                        # "client_id": JOBDIVA_CLIENT_ID,
                    },
                )
                resp.raise_for_status()
                body = resp.json()

            token = body.get("access_token") or body.get("token")
            expires_in = int(body.get("expires_in", 3600))
            _jd_token_cache["token"] = token
            _jd_token_cache["expires_at"] = time.time() + expires_in
            return {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            }

    raise RuntimeError("JobDiva credentials not configured in environment")


async def create_candidate_note(
    candidate_id: str, note_text: str, recruiter_id: Optional[str] = None
) -> dict:
    """
    Create a candidate note/journal entry in JobDiva.
    The actual endpoint/payload will depend on JobDiva API. Adjust below.
    """
    headers = await _get_jobdiva_headers()
    # Placeholder endpoint - replace with actual JobDiva endpoint from their docs
    url = f"{JOBDIVA_BASE_URL}/apiv2/candidates/{candidate_id}/notes"
    payload = {"noteText": note_text}
    if recruiter_id:
        payload["recruiterId"] = recruiter_id

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        return resp.json()


async def find_candidate_by_phone(phone_e164: str) -> Optional[dict]:
    """
    Search JobDiva for a candidate by phone.
    Adjust the endpoint/payload to match JobDiva's search API.
    """
    headers = await _get_jobdiva_headers()
    # Placeholder; confirm the actual search endpoint and payload
    url = f"{JOBDIVA_BASE_URL}/apiv2/candidates/search"
    payload = {"phone": phone_e164}
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(url, json=payload, headers=headers)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        j = resp.json()

    # adapt this depending on JobDiva's response shape
    candidates = j.get("candidates") or j.get("items") or j
    if not candidates:
        return None
    if isinstance(candidates, list):
        return candidates[0]
    return candidates


class JobDivaService:
    """
    Thin wrapper class so routes can use `jobdiva_service.method(...)`.
    """

    async def create_candidate_note(
        self, candidate_id: str, note_text: str, recruiter_id: Optional[str] = None
    ) -> dict:
        return await create_candidate_note(candidate_id, note_text, recruiter_id)

    async def find_candidate_by_phone(self, phone_e164: str) -> Optional[dict]:
        return await find_candidate_by_phone(phone_e164)


# This is what routes import: from services.jobdiva_service import jobdiva_service
jobdiva_service = JobDivaService()
