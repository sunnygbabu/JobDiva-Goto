from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging
from datetime import datetime, timezone
import os

from models.bridge_models import CallStartRequest, CallStartResponse
from models.mapping_models import InteractionLog
from services.goto_service import goto_service
from services.jobdiva_service import jobdiva_service
from utils.phone_utils import normalize_phone_e164

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/call", tags=["Calls"])

async def get_db() -> AsyncIOMotorDatabase:
    from motor.motor_asyncio import AsyncIOMotorClient
    client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    return client[os.environ['DB_NAME']]

@router.post("/start", response_model=CallStartResponse)
async def start_call(request: CallStartRequest):
    """
    Initiate a call from recruiter to candidate via GoTo Connect.
    
    Flow:
    1. Normalize phone numbers
    2. Look up recruiter's GoTo phone number and user ID
    3. Initiate call via GoTo Connect API
    4. Create candidate note in JobDiva
    5. Log interaction in database
    """
    try:
        db = await get_db()
        
        # Normalize phone numbers
        candidate_phone = normalize_phone_e164(request.candidate_phone)
        
        # Look up recruiter's GoTo mapping
        mapping = await db.user_mappings.find_one({
            "jobdiva_user_id": request.recruiter_id or request.recruiter_name,
            "is_active": True
        }, {"_id": 0})
        
        if not mapping:
            logger.warning(f"No mapping found for recruiter {request.recruiter_name}. Using mock data.")
            recruiter_phone = "+14155551000"
            goto_user_id = "mock_user_id"
        else:
            recruiter_phone = mapping["goto_phone_number"]
            goto_user_id = mapping["goto_user_id"]
        
        logger.info(f"Initiating call from {recruiter_phone} to {candidate_phone}")
        
        # Initiate call via GoTo Connect
        goto_result = await goto_service.initiate_call(
            from_phone=recruiter_phone,
            to_phone=candidate_phone,
            goto_user_id=goto_user_id
        )
        
        if not goto_result["success"]:
            raise HTTPException(status_code=500, detail="Failed to initiate call via GoTo Connect")
        
        call_method = goto_result.get("method", "api")
        tel_uri = None
        
        if call_method == "tel_fallback":
            tel_uri = f"tel:{candidate_phone}"
        
        # Create candidate note in JobDiva
        note_text = (
            f"[GoTo][Call][Outbound Attempt] Recruiter: {request.recruiter_name} ({recruiter_phone}) → "
            f"Candidate: {candidate_phone}\n"
            f"Time: {goto_result['timestamp']}\n"
            f"Status: Initiated\n"
            f"Call ID: {goto_result.get('call_id', 'N/A')}"
        )
        
        jobdiva_note_created = False
        jobdiva_note_id = None
        jobdiva_error = None
        
        if request.candidate_id:
            try:
                note_result = await jobdiva_service.create_candidate_note(
                    candidate_id=request.candidate_id,
                    note_text=note_text
                )
                jobdiva_note_created = note_result["success"]
                jobdiva_note_id = note_result.get("note_id")
            except Exception as e:
                logger.error(f"Failed to create JobDiva note: {e}")
                jobdiva_error = str(e)
        
        # Log interaction
        interaction_log = InteractionLog(
            interaction_type="call",
            direction="outbound",
            candidate_id=request.candidate_id,
            candidate_name=request.candidate_name,
            candidate_phone=candidate_phone,
            recruiter_id=request.recruiter_id,
            recruiter_name=request.recruiter_name,
            recruiter_phone=recruiter_phone,
            goto_call_id=goto_result.get("call_id"),
            goto_session_id=goto_result.get("session_id"),
            status="initiated",
            jobdiva_note_created=jobdiva_note_created,
            jobdiva_note_id=jobdiva_note_id,
            jobdiva_note_error=jobdiva_error
        )
        
        log_dict = interaction_log.model_dump()
        log_dict['timestamp'] = log_dict['timestamp'].isoformat()
        await db.interaction_logs.insert_one(log_dict)
        
        return CallStartResponse(
            success=True,
            message="Call initiated successfully",
            interaction_log_id=interaction_log.id,
            goto_call_id=goto_result.get("call_id"),
            call_method=call_method,
            tel_uri=tel_uri,
            jobdiva_note_created=jobdiva_note_created,
            timestamp=datetime.now(timezone.utc)
        )
        
    except Exception as e:
        logger.error(f"Error initiating call: {e}")
        raise HTTPException(status_code=500, detail=str(e))
