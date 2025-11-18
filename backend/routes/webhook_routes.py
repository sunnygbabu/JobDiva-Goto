from fastapi import APIRouter, HTTPException, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging
from datetime import datetime, timezone
import os

from models.bridge_models import GoToMessageEvent, GoToCallEvent, WebhookResponse
from models.mapping_models import InteractionLog
from services.goto_service import goto_service
from services.jobdiva_service import jobdiva_service
from utils.phone_utils import normalize_phone_e164

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks/goto", tags=["Webhooks"])

async def get_db() -> AsyncIOMotorDatabase:
    from motor.motor_asyncio import AsyncIOMotorClient
    client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    return client[os.environ['DB_NAME']]

@router.post("/messages", response_model=WebhookResponse)
async def handle_message_webhook(event: GoToMessageEvent):
    """
    Handle incoming/outbound SMS events from GoTo Connect.
    
    Flow:
    1. Normalize phone numbers
    2. Determine direction and participants
    3. Find candidate by phone number
    4. Create candidate note in JobDiva
    5. Log interaction
    """
    try:
        db = await get_db()
        
        # Normalize phone numbers
        from_phone = normalize_phone_e164(event.from_number)
        to_phone = normalize_phone_e164(event.to_number)
        
        logger.info(f"Processing SMS webhook: {event.direction} from {from_phone} to {to_phone}")
        
        # Determine if this is inbound or outbound
        # Inbound: from candidate to recruiter
        # Outbound: from recruiter to candidate (delivery status update)
        
        # Check if we have a mapping for either number
        recruiter_mapping = await db.user_mappings.find_one({
            "goto_phone_number": to_phone if event.direction == "inbound" else from_phone,
            "is_active": True
        }, {"_id": 0})
        
        if event.direction == "inbound":
            candidate_phone = from_phone
            recruiter_phone = to_phone
            recruiter_name = recruiter_mapping["jobdiva_user_name"] if recruiter_mapping else "Unknown Recruiter"
            recruiter_id = recruiter_mapping["jobdiva_user_id"] if recruiter_mapping else None
        else:
            candidate_phone = to_phone
            recruiter_phone = from_phone
            recruiter_name = recruiter_mapping["jobdiva_user_name"] if recruiter_mapping else "Unknown Recruiter"
            recruiter_id = recruiter_mapping["jobdiva_user_id"] if recruiter_mapping else None
        
        # Find candidate by phone
        candidate = await jobdiva_service.find_candidate_by_phone(candidate_phone)
        
        if not candidate:
            logger.warning(f"No candidate found for phone {candidate_phone}")
            candidate_id = None
            candidate_name = "Unknown Candidate"
        else:
            candidate_id = candidate["candidate_id"]
            candidate_name = candidate["candidate_name"]
        
        # Create candidate note in JobDiva
        if event.direction == "inbound":
            note_text = (
                f"[GoTo][SMS][Inbound] Candidate: {from_phone} → Recruiter: {recruiter_name} ({to_phone})\n"
                f"Message: \"{event.body}\"\n"
                f"Received: {event.timestamp}"
            )
        else:
            note_text = (
                f"[GoTo][SMS][Outbound Status] Recruiter: {recruiter_name} ({from_phone}) → Candidate: {to_phone}\n"
                f"Status: {event.status}\n"
                f"Updated: {event.timestamp}"
            )
        
        jobdiva_note_created = False
        jobdiva_note_id = None
        
        if candidate_id:
            try:
                note_result = await jobdiva_service.create_candidate_note(
                    candidate_id=candidate_id,
                    note_text=note_text
                )
                jobdiva_note_created = note_result["success"]
                jobdiva_note_id = note_result.get("note_id")
            except Exception as e:
                logger.error(f"Failed to create JobDiva note: {e}")
        
        # Log interaction
        interaction_log = InteractionLog(
            interaction_type="sms",
            direction=event.direction,
            candidate_id=candidate_id,
            candidate_name=candidate_name,
            candidate_phone=candidate_phone,
            recruiter_id=recruiter_id,
            recruiter_name=recruiter_name,
            recruiter_phone=recruiter_phone,
            goto_message_id=event.message_id,
            message_body=event.body,
            status=event.status,
            jobdiva_note_created=jobdiva_note_created,
            jobdiva_note_id=jobdiva_note_id
        )
        
        log_dict = interaction_log.model_dump()
        log_dict['timestamp'] = log_dict['timestamp'].isoformat()
        await db.interaction_logs.insert_one(log_dict)
        
        return WebhookResponse(
            success=True,
            message="Message webhook processed successfully",
            processed=True,
            interaction_log_id=interaction_log.id
        )
        
    except Exception as e:
        logger.error(f"Error processing message webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/call-events", response_model=WebhookResponse)
async def handle_call_webhook(event: GoToCallEvent):
    """
    Handle call event webhooks from GoTo Connect.
    
    Flow:
    1. Normalize phone numbers
    2. Determine direction and participants
    3. Fetch full call details if needed
    4. Find candidate by phone number
    5. Create candidate note in JobDiva
    6. Update or create interaction log
    """
    try:
        db = await get_db()
        
        # Normalize phone numbers
        from_phone = normalize_phone_e164(event.from_number)
        to_phone = normalize_phone_e164(event.to_number)
        
        logger.info(f"Processing call webhook: {event.direction} from {from_phone} to {to_phone}")
        
        # Determine participants
        recruiter_mapping = await db.user_mappings.find_one({
            "goto_phone_number": from_phone if event.direction == "outbound" else to_phone,
            "is_active": True
        }, {"_id": 0})
        
        if event.direction == "outbound":
            candidate_phone = to_phone
            recruiter_phone = from_phone
        else:
            candidate_phone = from_phone
            recruiter_phone = to_phone
        
        recruiter_name = recruiter_mapping["jobdiva_user_name"] if recruiter_mapping else "Unknown Recruiter"
        recruiter_id = recruiter_mapping["jobdiva_user_id"] if recruiter_mapping else None
        
        # Find candidate
        candidate = await jobdiva_service.find_candidate_by_phone(candidate_phone)
        
        if not candidate:
            logger.warning(f"No candidate found for phone {candidate_phone}")
            candidate_id = None
            candidate_name = "Unknown Candidate"
        else:
            candidate_id = candidate["candidate_id"]
            candidate_name = candidate["candidate_name"]
        
        # Format duration
        duration_str = f"{event.duration} seconds" if event.duration else "N/A"
        
        # Create candidate note
        if event.direction == "outbound":
            note_text = (
                f"[GoTo][Call][Outbound] Recruiter: {recruiter_name} ({from_phone}) → Candidate: {to_phone}\n"
                f"Result: {event.call_result} | Duration: {duration_str}\n"
                f"Time: {event.start_time}"
            )
        else:
            note_text = (
                f"[GoTo][Call][Inbound] Candidate: {from_phone} → Recruiter: {recruiter_name} ({to_phone})\n"
                f"Result: {event.call_result} | Duration: {duration_str}\n"
                f"Time: {event.start_time}"
            )
        
        jobdiva_note_created = False
        jobdiva_note_id = None
        
        if candidate_id:
            try:
                note_result = await jobdiva_service.create_candidate_note(
                    candidate_id=candidate_id,
                    note_text=note_text
                )
                jobdiva_note_created = note_result["success"]
                jobdiva_note_id = note_result.get("note_id")
            except Exception as e:
                logger.error(f"Failed to create JobDiva note: {e}")
        
        # Check if we already have a log for this call (from initiation)
        existing_log = await db.interaction_logs.find_one({
            "goto_call_id": event.call_id
        }, {"_id": 0})
        
        if existing_log:
            # Update existing log
            await db.interaction_logs.update_one(
                {"id": existing_log["id"]},
                {"$set": {
                    "call_duration": event.duration,
                    "call_result": event.call_result,
                    "status": "completed",
                    "jobdiva_note_created": jobdiva_note_created or existing_log.get("jobdiva_note_created", False),
                    "jobdiva_note_id": jobdiva_note_id or existing_log.get("jobdiva_note_id")
                }}
            )
            interaction_log_id = existing_log["id"]
        else:
            # Create new log
            interaction_log = InteractionLog(
                interaction_type="call",
                direction=event.direction,
                candidate_id=candidate_id,
                candidate_name=candidate_name,
                candidate_phone=candidate_phone,
                recruiter_id=recruiter_id,
                recruiter_name=recruiter_name,
                recruiter_phone=recruiter_phone,
                goto_call_id=event.call_id,
                goto_session_id=event.session_id,
                call_duration=event.duration,
                call_result=event.call_result,
                status="completed",
                jobdiva_note_created=jobdiva_note_created,
                jobdiva_note_id=jobdiva_note_id
            )
            
            log_dict = interaction_log.model_dump()
            log_dict['timestamp'] = log_dict['timestamp'].isoformat()
            await db.interaction_logs.insert_one(log_dict)
            interaction_log_id = interaction_log.id
        
        return WebhookResponse(
            success=True,
            message="Call webhook processed successfully",
            processed=True,
            interaction_log_id=interaction_log_id
        )
        
    except Exception as e:
        logger.error(f"Error processing call webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))
