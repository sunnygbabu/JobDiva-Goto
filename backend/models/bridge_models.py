from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# SMS Models
class SMSSendRequest(BaseModel):
    """
    Request to send SMS from Chrome extension.
    """
    candidate_id: Optional[str] = None
    candidate_name: str
    candidate_phone: str
    recruiter_id: Optional[str] = None
    recruiter_name: str
    message: str

class SMSSendResponse(BaseModel):
    """
    Response after sending SMS.
    """
    success: bool
    message: str
    interaction_log_id: str
    goto_message_id: Optional[str] = None
    jobdiva_note_created: bool
    timestamp: datetime

# Call Models
class CallStartRequest(BaseModel):
    """
    Request to initiate a call from Chrome extension.
    """
    candidate_id: Optional[str] = None
    candidate_name: str
    candidate_phone: str
    recruiter_id: Optional[str] = None
    recruiter_name: str

class CallStartResponse(BaseModel):
    """
    Response after initiating call.
    """
    success: bool
    message: str
    interaction_log_id: str
    goto_call_id: Optional[str] = None
    call_method: str  # "api" or "tel_fallback"
    tel_uri: Optional[str] = None
    jobdiva_note_created: bool
    timestamp: datetime

# Webhook Models
class GoToMessageEvent(BaseModel):
    """
    GoTo Connect message webhook event.
    """
    message_id: str
    from_number: str
    to_number: str
    body: str
    direction: str  # "inbound" or "outbound"
    status: str  # "sent", "delivered", "failed"
    timestamp: str

class GoToCallEvent(BaseModel):
    """
    GoTo Connect call webhook event.
    """
    call_id: str
    session_id: Optional[str] = None
    from_number: str
    to_number: str
    direction: str  # "inbound" or "outbound"
    call_result: str  # "answered", "missed", "voicemail", "busy"
    duration: Optional[int] = None  # seconds
    start_time: str
    end_time: Optional[str] = None

class WebhookResponse(BaseModel):
    """
    Standard webhook response.
    """
    success: bool
    message: str
    processed: bool
    interaction_log_id: Optional[str] = None
