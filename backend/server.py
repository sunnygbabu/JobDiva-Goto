# server.py

from fastapi import FastAPI, APIRouter
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List
import uuid
from datetime import datetime, timezone

# Import route modules
from routes import sms_routes, call_routes, webhook_routes, admin_routes

# OPTIONAL: debug helper to verify GoTo token, adjust import path as needed
# If goto_service.py is in a "services" package:
# from services.goto_service import debug_get_raw_access_token
# If it's in the same folder as server.py:
# from goto_service import debug_get_raw_access_token

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

# MongoDB connection
mongo_url = os.getenv("MONGO_URL")
if not mongo_url:
    raise RuntimeError("MONGO_URL is not set. Check your .env or environment variables.")

db_name = os.getenv("DB_NAME")
if not db_name:
    raise RuntimeError("DB_NAME is not set. Check your .env or environment variables.")
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ["DB_NAME"]]

# Create the main app without a prefix
app = FastAPI(
    title="JobDiva-GoTo Bridge API",
    description="Bridge service for integrating JobDiva ATS with GoTo Connect",
    version="1.0.0",
)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# ------------------ Models ------------------


class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")  # Ignore MongoDB's _id field

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class StatusCheckCreate(BaseModel):
    client_name: str


# ------------------ Routes ------------------


@api_router.get("/")
async def root():
    return {
        "message": "JobDiva-GoTo Bridge API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "sms": "/api/sms/send",
            "call": "/api/call/start",
            "webhooks": {
                "messages": "/api/webhooks/goto/messages",
                "calls": "/api/webhooks/goto/call-events",
            },
            "admin": {
                "mappings": "/api/admin/mappings",
                "logs": "/api/admin/logs",
            },
        },
    }


@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)

    # Convert to dict and serialize datetime to ISO string for MongoDB
    doc = status_obj.model_dump()
    doc["timestamp"] = doc["timestamp"].isoformat()

    await db.status_checks.insert_one(doc)
    return status_obj


@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    # Exclude MongoDB's _id field from the query results
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)

    # Convert ISO string timestamps back to datetime objects
    for check in status_checks:
        if isinstance(check["timestamp"], str):
            check["timestamp"] = datetime.fromisoformat(check["timestamp"])

    return status_checks


# OPTIONAL: debug route to verify GoTo token (remove in prod)
# Uncomment and adjust import if you want this.
#
# @api_router.get("/debug/goto/token")
# async def debug_goto_token():
#     token = await debug_get_raw_access_token()
#     # Don't print full token in real logs; this is for local debugging only.
#     return {"access_token": token}


# Include bridge service routes
api_router.include_router(sms_routes.router)
api_router.include_router(call_routes.router)
api_router.include_router(webhook_routes.router)
api_router.include_router(admin_routes.router)

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
