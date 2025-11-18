from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
import logging
from datetime import datetime, timezone
import os

from models.mapping_models import UserMapping, UserMappingCreate, UserMappingUpdate, InteractionLog
from utils.phone_utils import normalize_phone_e164

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"])

async def get_db() -> AsyncIOMotorDatabase:
    from motor.motor_asyncio import AsyncIOMotorClient
    client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    return client[os.environ['DB_NAME']]

# User Mappings
@router.post("/mappings", response_model=UserMapping)
async def create_mapping(mapping: UserMappingCreate):
    """
    Create a new JobDiva <-> GoTo user mapping.
    """
    try:
        db = await get_db()
        
        # Normalize phone number
        normalized_phone = normalize_phone_e164(mapping.goto_phone_number)
        
        # Check if mapping already exists
        existing = await db.user_mappings.find_one({
            "jobdiva_user_id": mapping.jobdiva_user_id
        }, {"_id": 0})
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Mapping already exists for JobDiva user {mapping.jobdiva_user_id}"
            )
        
        # Create mapping
        user_mapping = UserMapping(
            jobdiva_user_id=mapping.jobdiva_user_id,
            jobdiva_user_name=mapping.jobdiva_user_name,
            goto_user_id=mapping.goto_user_id,
            goto_phone_number=normalized_phone,
            goto_extension=mapping.goto_extension
        )
        
        mapping_dict = user_mapping.model_dump()
        mapping_dict['created_at'] = mapping_dict['created_at'].isoformat()
        mapping_dict['updated_at'] = mapping_dict['updated_at'].isoformat()
        
        await db.user_mappings.insert_one(mapping_dict)
        
        logger.info(f"Created mapping for {mapping.jobdiva_user_name}")
        
        return user_mapping
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating mapping: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/mappings", response_model=List[UserMapping])
async def list_mappings(active_only: bool = False):
    """
    List all user mappings.
    """
    try:
        db = await get_db()
        
        query = {"is_active": True} if active_only else {}
        mappings = await db.user_mappings.find(query, {"_id": 0}).to_list(1000)
        
        # Convert ISO strings back to datetime
        for mapping in mappings:
            if isinstance(mapping.get('created_at'), str):
                mapping['created_at'] = datetime.fromisoformat(mapping['created_at'])
            if isinstance(mapping.get('updated_at'), str):
                mapping['updated_at'] = datetime.fromisoformat(mapping['updated_at'])
        
        return mappings
        
    except Exception as e:
        logger.error(f"Error listing mappings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/mappings/{jobdiva_user_id}", response_model=UserMapping)
async def get_mapping(jobdiva_user_id: str):
    """
    Get a specific user mapping.
    """
    try:
        db = await get_db()
        
        mapping = await db.user_mappings.find_one({
            "jobdiva_user_id": jobdiva_user_id
        }, {"_id": 0})
        
        if not mapping:
            raise HTTPException(status_code=404, detail="Mapping not found")
        
        # Convert ISO strings
        if isinstance(mapping.get('created_at'), str):
            mapping['created_at'] = datetime.fromisoformat(mapping['created_at'])
        if isinstance(mapping.get('updated_at'), str):
            mapping['updated_at'] = datetime.fromisoformat(mapping['updated_at'])
        
        return mapping
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting mapping: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/mappings/{jobdiva_user_id}", response_model=UserMapping)
async def update_mapping(jobdiva_user_id: str, update: UserMappingUpdate):
    """
    Update a user mapping.
    """
    try:
        db = await get_db()
        
        mapping = await db.user_mappings.find_one({
            "jobdiva_user_id": jobdiva_user_id
        }, {"_id": 0})
        
        if not mapping:
            raise HTTPException(status_code=404, detail="Mapping not found")
        
        # Prepare update data
        update_data = update.model_dump(exclude_unset=True)
        
        if "goto_phone_number" in update_data:
            update_data["goto_phone_number"] = normalize_phone_e164(update_data["goto_phone_number"])
        
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        await db.user_mappings.update_one(
            {"jobdiva_user_id": jobdiva_user_id},
            {"$set": update_data}
        )
        
        # Fetch updated mapping
        updated_mapping = await db.user_mappings.find_one({
            "jobdiva_user_id": jobdiva_user_id
        }, {"_id": 0})
        
        # Convert ISO strings
        if isinstance(updated_mapping.get('created_at'), str):
            updated_mapping['created_at'] = datetime.fromisoformat(updated_mapping['created_at'])
        if isinstance(updated_mapping.get('updated_at'), str):
            updated_mapping['updated_at'] = datetime.fromisoformat(updated_mapping['updated_at'])
        
        return updated_mapping
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating mapping: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/mappings/{jobdiva_user_id}")
async def delete_mapping(jobdiva_user_id: str):
    """
    Soft delete a user mapping (sets is_active to False).
    """
    try:
        db = await get_db()
        
        result = await db.user_mappings.update_one(
            {"jobdiva_user_id": jobdiva_user_id},
            {"$set": {
                "is_active": False,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Mapping not found")
        
        return {"success": True, "message": "Mapping deactivated"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting mapping: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Interaction Logs
@router.get("/logs", response_model=List[InteractionLog])
async def list_interaction_logs(
    limit: int = 100,
    interaction_type: str = None,
    candidate_id: str = None
):
    """
    List interaction logs with optional filtering.
    """
    try:
        db = await get_db()
        
        query = {}
        if interaction_type:
            query["interaction_type"] = interaction_type
        if candidate_id:
            query["candidate_id"] = candidate_id
        
        logs = await db.interaction_logs.find(
            query,
            {"_id": 0}
        ).sort("timestamp", -1).limit(limit).to_list(limit)
        
        # Convert ISO strings
        for log in logs:
            if isinstance(log.get('timestamp'), str):
                log['timestamp'] = datetime.fromisoformat(log['timestamp'])
        
        return logs
        
    except Exception as e:
        logger.error(f"Error listing logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs/{log_id}", response_model=InteractionLog)
async def get_interaction_log(log_id: str):
    """
    Get a specific interaction log.
    """
    try:
        db = await get_db()
        
        log = await db.interaction_logs.find_one({"id": log_id}, {"_id": 0})
        
        if not log:
            raise HTTPException(status_code=404, detail="Log not found")
        
        if isinstance(log.get('timestamp'), str):
            log['timestamp'] = datetime.fromisoformat(log['timestamp'])
        
        return log
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting log: {e}")
        raise HTTPException(status_code=500, detail=str(e))
