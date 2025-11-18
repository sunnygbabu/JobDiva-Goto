from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime, timezone
import uuid

class UserMapping(BaseModel):
    """
    Mapping between JobDiva user and GoTo Connect user/phone.
    """
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    jobdiva_user_id: str
    jobdiva_user_name: str
    goto_user_id: str
    goto_phone_number: str  # E.164 format
    goto_extension: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserMappingCreate(BaseModel):
    """
    Request model for creating a user mapping.
    """
    jobdiva_user_id: str
    jobdiva_user_name: str
    goto_user_id: str
    goto_phone_number: str
    goto_extension: Optional[str] = None

class UserMappingUpdate(BaseModel):
    """
    Request model for updating a user mapping.
    """
    goto_user_id: Optional[str] = None
    goto_phone_number: Optional[str] = None
    goto_extension: Optional[str] = None
    is_active: Optional[bool] = None

class InteractionLog(BaseModel):
    """
    Log entry for call/SMS interactions.
    """
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    interaction_type: str  # "sms" or "call"
    direction: str  # "inbound" or "outbound"
    
    # JobDiva info
    candidate_id: Optional[str] = None
    candidate_name: str
    candidate_phone: str
    
    recruiter_id: Optional[str] = None
    recruiter_name: str
    recruiter_phone: str
    
    # GoTo info
    goto_message_id: Optional[str] = None
    goto_call_id: Optional[str] = None
    goto_session_id: Optional[str] = None
    
    # Content
    message_body: Optional[str] = None
    call_duration: Optional[int] = None  # seconds
    call_result: Optional[str] = None  # "answered", "missed", "voicemail"
    
    status: str  # "sent", "delivered", "failed", "completed", etc.
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # JobDiva note info
    jobdiva_note_created: bool = False
    jobdiva_note_id: Optional[str] = None
    jobdiva_note_error: Optional[str] = None
