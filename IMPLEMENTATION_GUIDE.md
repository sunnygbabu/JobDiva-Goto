# JobDiva-GoTo Bridge Service - Implementation Guide

## Overview

This is a complete bridge service that integrates JobDiva ATS with GoTo Connect for seamless call and SMS communication. The service includes:

1. **Backend API** (Python/FastAPI) - Bridge service with mocked APIs
2. **Admin Dashboard** (React) - Manage user mappings and view interaction logs
3. **Chrome Extension** - Inject call/SMS buttons into JobDiva pages

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    JobDiva Web Pages                    │
│              (Chrome Extension Injected)                │
└───────────────────────┬─────────────────────────────────┘
                        │ API Calls (JSON)
                        ▼
┌─────────────────────────────────────────────────────────┐
│              FastAPI Bridge Service (Python)            │
│  ┌────────────────────────────────────────────────┐    │
│  │  API Endpoints:                                │    │
│  │  • POST /api/sms/send                          │    │
│  │  • POST /api/call/start                        │    │
│  │  • POST /api/webhooks/goto/messages            │    │
│  │  • POST /api/webhooks/goto/call-events         │    │
│  │  • GET/POST /api/admin/mappings                │    │
│  │  • GET /api/admin/logs                         │    │
│  └────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────┐    │
│  │  Services (Currently MOCKED):                  │    │
│  │  • GoTo Connect Service (OAuth, SMS, Calls)    │    │
│  │  • JobDiva Service (Candidate notes, search)   │    │
│  └────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────┐    │
│  │  Database (MongoDB):                           │    │
│  │  • user_mappings - JobDiva ↔ GoTo mapping     │    │
│  │  • interaction_logs - Call/SMS history         │    │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

## Current Status

### ✅ Fully Implemented

1. **Backend API**
   - All 6 main endpoints functional
   - Phone number normalization (E.164)
   - Interaction logging
   - User mapping management
   - Error handling and validation

2. **Admin Dashboard**
   - User mapping management UI
   - Interaction log viewer
   - Real-time data from API
   - Responsive design

3. **Chrome Extension**
   - Manifest v3 compliant
   - Content script for JobDiva pages
   - Call and SMS buttons
   - SMS modal interface
   - Configuration popup

### ⚠️ Currently Mocked (Need Real Implementation)

1. **GoTo Connect Integration**
   - Location: `/app/backend/services/goto_service.py`
   - Mocked functions:
     - `authenticate()` - OAuth2 authentication
     - `send_sms()` - SMS sending
     - `initiate_call()` - Call initiation
     - `get_call_events()` - Fetch call details

2. **JobDiva Integration**
   - Location: `/app/backend/services/jobdiva_service.py`
   - Mocked functions:
     - `authenticate()` - API authentication
     - `create_candidate_note()` - Create journal notes
     - `find_candidate_by_phone()` - Search candidates
     - `get_candidate()` - Fetch candidate details

## File Structure

```
/app/
├── backend/
│   ├── server.py                 # Main FastAPI application
│   ├── requirements.txt          # Python dependencies
│   ├── .env                      # Environment variables
│   ├── models/
│   │   ├── bridge_models.py      # API request/response models
│   │   └── mapping_models.py     # User mapping & log models
│   ├── services/
│   │   ├── goto_service.py       # GoTo Connect integration (MOCKED)
│   │   └── jobdiva_service.py    # JobDiva integration (MOCKED)
│   ├── routes/
│   │   ├── sms_routes.py         # SMS endpoints
│   │   ├── call_routes.py        # Call endpoints
│   │   ├── webhook_routes.py     # Webhook handlers
│   │   └── admin_routes.py       # Admin endpoints
│   └── utils/
│       └── phone_utils.py        # Phone number utilities
├── frontend/
│   ├── src/
│   │   ├── App.js                # Main React app
│   │   ├── pages/
│   │   │   └── AdminPage.js      # Admin dashboard page
│   │   └── components/
│   │       ├── MappingManager.js # User mapping manager
│   │       └── InteractionLog.js # Interaction log viewer
│   ├── package.json
│   └── .env                      # Frontend env vars
└── chrome-extension/
    ├── manifest.json             # Extension manifest (v3)
    ├── content.js                # Runs on JobDiva pages
    ├── background.js             # Service worker
    ├── popup.html                # Extension popup UI
    ├── popup.js                  # Popup logic
    ├── styles.css                # Injected styles
    ├── icon16.png                # Extension icons (placeholder)
    ├── icon48.png
    ├── icon128.png
    └── README.md                 # Extension documentation
```

## Setup & Testing

### Backend

The backend is already running and tested. Key endpoints:

```bash
# Test API health
curl http://localhost:8001/api/

# Create a user mapping
curl -X POST http://localhost:8001/api/admin/mappings \
  -H "Content-Type: application/json" \
  -d '{
    "jobdiva_user_id": "jd_user_001",
    "jobdiva_user_name": "Alice Johnson",
    "goto_user_id": "goto_user_001",
    "goto_phone_number": "+14155551001"
  }'

# Send SMS (mocked)
curl -X POST http://localhost:8001/api/sms/send \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_id": "cand_12345",
    "candidate_name": "John Doe",
    "candidate_phone": "+14155552671",
    "recruiter_id": "jd_user_001",
    "recruiter_name": "Alice Johnson",
    "message": "Hi John, this is Alice from ABC Recruiting!"
  }'
```

### Frontend

```bash
# Frontend is running at port 3000
# Access at: http://localhost:3000
# Admin Dashboard: http://localhost:3000/admin
```

### Chrome Extension

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select the `/app/chrome-extension` folder
5. Click extension icon to configure

## Replacing Mocked APIs with Real Implementation

### GoTo Connect Integration

**File**: `/app/backend/services/goto_service.py`

#### 1. Authentication

```python
async def authenticate(self, client_id: str, client_secret: str) -> bool:
    """
    REAL Implementation:
    POST https://authentication.logmeininc.com/oauth/token
    Headers:
        Content-Type: application/x-www-form-urlencoded
    Body:
        grant_type=client_credentials
        client_id={client_id}
        client_secret={client_secret}
    
    Store access_token and token_expires_at
    """
    # Replace MOCKED code here
```

#### 2. Send SMS

```python
async def send_sms(self, from_phone: str, to_phone: str, message: str) -> Dict[str, Any]:
    """
    REAL Implementation:
    POST https://api.goto.com/messaging/v1/messages
    Headers:
        Authorization: Bearer {access_token}
        Content-Type: application/json
    Body:
        {
            "ownerPhoneNumber": from_phone,
            "contactPhoneNumbers": [to_phone],
            "body": message
        }
    
    Response:
        {
            "id": "message_id",
            "status": "sent",
            ...
        }
    """
    # Replace MOCKED code here
```

#### 3. Initiate Call

```python
async def initiate_call(self, from_phone: str, to_phone: str, goto_user_id: str = None) -> Dict[str, Any]:
    """
    REAL Implementation:
    Option 1: Click-to-Call API (if available)
    POST https://api.goto.com/voice/v1/calls
    
    Option 2: Devices API
    POST https://api.goto.com/voice/v1/devices/{deviceId}/calls
    Headers:
        Authorization: Bearer {access_token}
    Body:
        {
            "phoneNumber": to_phone
        }
    
    Option 3: Fallback to tel: URI
    Return tel_uri for manual dialing
    """
    # Replace MOCKED code here
```

**Environment Variables Needed**:

Add to `/app/backend/.env`:
```
GOTO_CLIENT_ID=your_goto_client_id
GOTO_CLIENT_SECRET=your_goto_client_secret
GOTO_API_BASE_URL=https://api.goto.com
```

### JobDiva Integration

**File**: `/app/backend/services/jobdiva_service.py`

#### 1. Authentication

```python
async def authenticate(self, api_key: str, base_url: str) -> bool:
    """
    REAL Implementation:
    Depends on JobDiva's authentication method.
    Could be:
    - API Key in headers
    - OAuth2
    - Session-based auth
    
    Check JobDiva API documentation for exact method.
    """
    # Replace MOCKED code here
```

#### 2. Create Candidate Note

```python
async def create_candidate_note(self, candidate_id: str, note_text: str, note_type: str = "General") -> Dict[str, Any]:
    """
    REAL Implementation:
    POST {base_url}/api/v1/candidates/{candidate_id}/notes
    Headers:
        Authorization: Bearer {api_key} (or appropriate auth)
        Content-Type: application/json
    Body:
        {
            "noteText": note_text,
            "noteType": note_type,
            "timestamp": "2025-01-10T12:00:00Z"
        }
    
    Check JobDiva API docs for exact endpoint and payload structure.
    """
    # Replace MOCKED code here
```

#### 3. Find Candidate by Phone

```python
async def find_candidate_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
    """
    REAL Implementation:
    GET {base_url}/api/v1/candidates/search?phone={phone}
    Headers:
        Authorization: Bearer {api_key}
    
    Response:
        {
            "candidateId": "...",
            "candidateName": "...",
            ...
        }
    """
    # Replace MOCKED code here
```

**Environment Variables Needed**:

Add to `/app/backend/.env`:
```
JOBDIVA_API_KEY=your_jobdiva_api_key
JOBDIVA_BASE_URL=https://api.jobdiva.com
# Or whatever JobDiva provides
```

## Webhook Configuration

### GoTo Connect Webhooks

Once you have real GoTo credentials:

1. **Configure webhook URLs** in GoTo Connect admin:
   - Message webhooks: `https://your-domain.com/api/webhooks/goto/messages`
   - Call webhooks: `https://your-domain.com/api/webhooks/goto/call-events`

2. **Webhook signature verification** (add to webhook routes):
```python
def verify_goto_webhook_signature(request, signature):
    # Implement GoTo's signature verification
    # Check GoTo documentation for their method
    pass
```

## Chrome Extension Customization

### Adjusting for JobDiva Page Structure

**File**: `/app/chrome-extension/content.js`

The extension needs to extract candidate information from JobDiva pages. You'll need to adjust selectors based on actual JobDiva HTML structure:

```javascript
// In extractCandidateInfo() function, update these selectors:
const candidateNameElement = document.querySelector('[YOUR-ACTUAL-SELECTOR]');
const candidatePhoneElement = document.querySelector('[YOUR-ACTUAL-SELECTOR]');
const candidateIdElement = document.querySelector('[YOUR-ACTUAL-SELECTOR]');
```

**How to find selectors**:
1. Open a JobDiva candidate page
2. Right-click on candidate name → Inspect
3. Note the class names or data attributes
4. Update selectors in `content.js`

### Configuring Backend URL

Update in `/app/chrome-extension/content.js`:
```javascript
const BACKEND_API_URL = 'https://your-deployed-backend.com/api';
```

## Deployment

### Backend + Frontend (Web Application)

#### Option 1: Emergent Platform (Recommended)
1. Click "Preview" to test
2. Click "Deploy" when ready
3. Cost: 50 credits/month
4. Automatic HTTPS, environment management

#### Option 2: AWS Deployment

**Backend (FastAPI)**:
- AWS Elastic Beanstalk
- AWS Lambda + API Gateway (serverless)
- AWS EC2 (full control)

**Frontend (React)**:
- AWS S3 + CloudFront (static hosting)
- Include in backend (serve from FastAPI)

**Database**:
- MongoDB Atlas (managed MongoDB)
- AWS DocumentDB

### Chrome Extension

#### Development Installation:
1. Go to `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select `/app/chrome-extension` folder

#### Chrome Web Store Publication:
1. **Create proper icons** (16x16, 48x48, 128x128)
2. **Create privacy policy** (required by Chrome Web Store)
3. **Package extension**:
   ```bash
   cd /app/chrome-extension
   zip -r jobdiva-goto-bridge.zip * -x "*.DS_Store" -x "README.md"
   ```
4. **Submit to Chrome Web Store**:
   - Go to [Chrome Web Store Developer Dashboard](https://chrome.google.com/webstore/devconsole)
   - Pay $5 one-time developer fee (if first time)
   - Upload ZIP file
   - Fill in listing details
   - Submit for review (1-3 days typically)

## Testing Workflow

### Backend Testing

```bash
# 1. Create user mappings
curl -X POST http://localhost:8001/api/admin/mappings -H "Content-Type: application/json" -d '{...}'

# 2. Test SMS send
curl -X POST http://localhost:8001/api/sms/send -H "Content-Type: application/json" -d '{...}'

# 3. Test call initiation
curl -X POST http://localhost:8001/api/call/start -H "Content-Type: application/json" -d '{...}'

# 4. View logs
curl http://localhost:8001/api/admin/logs
```

### Frontend Testing

1. Open http://localhost:3000
2. Click "Go to Admin Dashboard"
3. Add user mappings
4. View interaction logs

### Chrome Extension Testing

1. Install extension in Chrome
2. Configure backend URL in popup
3. Navigate to any webpage (JobDiva page ideally)
4. Open browser console to see logs
5. Test button injection and API calls

## API Documentation

Full API documentation available at:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

### Key Endpoints

#### POST /api/sms/send
Send SMS from recruiter to candidate.

**Request**:
```json
{
  "candidate_id": "cand_12345",
  "candidate_name": "John Doe",
  "candidate_phone": "+14155552671",
  "recruiter_id": "jd_user_001",
  "recruiter_name": "Alice Johnson",
  "message": "Hi John, this is Alice..."
}
```

**Response**:
```json
{
  "success": true,
  "message": "SMS sent successfully",
  "interaction_log_id": "uuid",
  "goto_message_id": "msg_...",
  "jobdiva_note_created": true,
  "timestamp": "2025-01-10T12:00:00Z"
}
```

#### POST /api/call/start
Initiate call from recruiter to candidate.

**Request**:
```json
{
  "candidate_id": "cand_12345",
  "candidate_name": "John Doe",
  "candidate_phone": "+14155552671",
  "recruiter_id": "jd_user_001",
  "recruiter_name": "Alice Johnson"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Call initiated successfully",
  "interaction_log_id": "uuid",
  "goto_call_id": "call_...",
  "call_method": "api",
  "tel_uri": null,
  "jobdiva_note_created": true,
  "timestamp": "2025-01-10T12:00:00Z"
}
```

## Security Considerations

1. **API Authentication**: Add authentication to admin endpoints in production
2. **CORS Configuration**: Restrict CORS to known origins
3. **Webhook Signatures**: Verify webhook signatures from GoTo Connect
4. **Input Validation**: All inputs are validated via Pydantic models
5. **Rate Limiting**: Consider adding rate limiting for production
6. **Secrets Management**: Use environment variables for all credentials

## Troubleshooting

### Backend Issues

**Issue**: Backend won't start
```bash
# Check logs
tail -n 100 /var/log/supervisor/backend.*.log

# Check Python imports
cd /app/backend && python -c "from routes import sms_routes"
```

**Issue**: MongoDB connection failed
```bash
# Verify MongoDB is running
sudo systemctl status mongodb
# Or check environment variable
echo $MONGO_URL
```

### Frontend Issues

**Issue**: API calls failing
- Check REACT_APP_BACKEND_URL in `/app/frontend/.env`
- Verify backend is running
- Check for CORS errors in browser console

### Chrome Extension Issues

**Issue**: Buttons not appearing
- Check if on correct page (URL contains "candidate")
- Open browser console for error messages
- Verify content script is loading

**Issue**: API calls failing
- Check backend URL in extension popup
- Verify CORS is configured correctly
- Check network tab in DevTools

## Next Steps

1. **Get API Credentials**:
   - GoTo Connect: Client ID, Client Secret
   - JobDiva: API Key and documentation

2. **Replace Mocked Services**:
   - Update `goto_service.py` with real API calls
   - Update `jobdiva_service.py` with real API calls
   - Test each endpoint individually

3. **Configure Webhooks**:
   - Set up GoTo webhook URLs
   - Test webhook delivery

4. **Customize Chrome Extension**:
   - Adjust selectors for JobDiva pages
   - Test on real JobDiva candidate pages

5. **Deploy**:
   - Deploy backend and frontend
   - Publish Chrome extension to store

## Support & Documentation

- **Backend API Docs**: http://localhost:8001/docs
- **Chrome Extension**: See `/app/chrome-extension/README.md`
- **GoTo Connect API**: https://developer.goto.com/
- **JobDiva API**: Contact JobDiva for documentation

## Version

**Current Version**: 1.0.0

**Status**: Fully functional with mocked APIs. Ready for real API integration.
