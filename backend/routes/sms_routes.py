from fastapi import APIRouter, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import logging
from datetime import datetime, timezone
import os

from models.bridge_models import SMSSendRequest, SMSSendResponse
from models.mapping_models import InteractionLog
from services.goto_service import goto_service
from services.jobdiva_service import jobdiva_service
from utils.phone_utils import normalize_phone_e164

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sms", tags=["SMS"])

# Database dependency
async def get_db() -> AsyncIOMotorDatabase:
    from motor.motor_asyncio import AsyncIOMotorClient
    client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    return client[os.environ['DB_NAME']]

@router.post("/send", response_model=SMSSendResponse)
async def send_sms(request: SMSSendRequest):
    """
    Send SMS from recruiter to candidate via GoTo Connect.
    
    Flow:
    1. Normalize phone numbers
    2. Look up recruiter's GoTo phone number from mappings
    3. Send SMS via GoTo Connect API
    4. Create candidate note in JobDiva
    5. Log interaction in database
    """
    try:
        db = await get_db()
        
        # Normalize phone numbers
        candidate_phone = normalize_phone_e164(request.candidate_phone)
        
        # Look up recruiter's GoTo phone mapping
        mapping = await db.user_mappings.find_one({
            "jobdiva_user_id": request.recruiter_id or request.recruiter_name,
            "is_active": True
        }, {"_id": 0})
        
        if not mapping:
            # If no mapping found, use a default/mock number
            logger.warning(f"No mapping found for recruiter {request.recruiter_name}. Using mock number.")
            recruiter_phone = "+14155551000"  # Mock default
        else:
            recruiter_phone = mapping["goto_phone_number"]
        
        logger.info(f"Sending SMS from {recruiter_phone} to {candidate_phone}")
        
        # Send SMS via GoTo Connect
        goto_result = await goto_service.send_sms(
            from_phone=recruiter_phone,
            to_phone=candidate_phone,
            message=request.message
        )
        
        if not goto_result["success"]:
            raise HTTPException(status_code=500, detail="Failed to send SMS via GoTo Connect")
        
        # Create candidate note in JobDiva
        note_text = (
            f"[GoTo][SMS][Outbound] Recruiter: {request.recruiter_name} ({recruiter_phone}) → "
            f"Candidate: {candidate_phone}\n"
            f"Message: \"{request.message[:100]}{'...' if len(request.message) > 100 else ''}\"\n"
            f"Status: Sent at {goto_result['timestamp']}"
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
            interaction_type="sms",
            direction="outbound",
            candidate_id=request.candidate_id,
            candidate_name=request.candidate_name,
            candidate_phone=candidate_phone,
            recruiter_id=request.recruiter_id,
            recruiter_name=request.recruiter_name,
            recruiter_phone=recruiter_phone,
            goto_message_id=goto_result["message_id"],
            message_body=request.message,
            status=goto_result["status"],
            jobdiva_note_created=jobdiva_note_created,
            jobdiva_note_id=jobdiva_note_id,
            jobdiva_note_error=jobdiva_error
        )
        
        log_dict = interaction_log.model_dump()
        log_dict['timestamp'] = log_dict['timestamp'].isoformat()
        await db.interaction_logs.insert_one(log_dict)
        
        return SMSSendResponse(
            success=True,
            message="SMS sent successfully",
            interaction_log_id=interaction_log.id,
            goto_message_id=goto_result["message_id"],
            jobdiva_note_created=jobdiva_note_created,
            timestamp=datetime.now(timezone.utc)
        )
        
    except Exception as e:
        logger.error(f"Error sending SMS: {e}")
        raise HTTPException(status_code=500, detail=str(e))
