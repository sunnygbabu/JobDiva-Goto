from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from services.goto_service import goto_service, GoToError

router = APIRouter(prefix="/sms", tags=["sms"])


class SendSmsRequest(BaseModel):
    candidate_phone: str = Field(..., description="Candidate phone number")
    message: str = Field(..., description="SMS message body")
    candidate_name: str = Field(..., description="Candidate name (for logging)")
    recruiter_name: str = Field(..., description="Recruiter name (for logging)")
    from_phone: Optional[str] = Field(
        None,
        description="GoTo SMS-enabled number (if omitted, uses default configured number)",
    )
    employer_id: Optional[str] = Field(
        None,
        description="Optional employer/client id for logging",
    )


@router.post("/send")
async def send_sms_handler(payload: SendSmsRequest):
    """
    Send an SMS via GoTo and (optionally) log it in JobDiva as a journal entry.
    """

    # Use a default GoTo number if not provided in the request
    FROM_NUMBER_DEFAULT = "+17323531312"  # TODO: replace with your real GoTo SMS number

    owner_phone_number = payload.from_phone or FROM_NUMBER_DEFAULT

    try:
        # Map API fields -> GoTo API
        goto_response = await goto_service.send_sms(
            owner_phone_number=owner_phone_number,
            contact_phone_numbers=[payload.candidate_phone],
            body=payload.message,
        )

        # TODO: log to JobDiva here:
        # - candidate_phone / candidate_name
        # - recruiter_name
        # - employer_id
        # - message text
        # - GoTo message id from goto_response

        return {
            "status": "ok",
            "from": owner_phone_number,
            "to": payload.candidate_phone,
            "candidate_name": payload.candidate_name,
            "recruiter_name": payload.recruiter_name,
            "goto": goto_response,
        }

    except GoToError as e:
        # Controlled errors from GoTo (token refresh, SMS API, etc.)
        raise HTTPException(status_code=502, detail=str(e))

    except Exception as e:
        # Unexpected errors
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")