# JobDiva-GoTo Bridge Service

Complete integration service between JobDiva ATS and GoTo Connect for seamless calling and SMS communication.

## 🎯 What's Built

### 1. **Backend Bridge Service** (Python/FastAPI)
Complete REST API with 6 main endpoints for SMS, calls, webhooks, and admin functions. All business logic implemented with mocked external APIs (GoTo Connect & JobDiva).

**Status**: ✅ Fully functional and tested

### 2. **Admin Dashboard** (React)
Web-based admin interface for managing user mappings (JobDiva ↔ GoTo) and viewing interaction history.

**Status**: ✅ Complete with full CRUD operations

### 3. **Chrome Extension** (Manifest v3)
Browser extension that injects "Call via GoTo" and "Text via GoTo" buttons on JobDiva candidate pages.

**Status**: ✅ Complete and ready for testing

## 🚀 Quick Start

### Access the Application

1. **Admin Dashboard**: 
   - Local: http://localhost:3000/admin
   - Deployed: https://recruiter-bridge.preview.emergentagent.com/admin

2. **API Documentation**:
   - Local: http://localhost:8001/docs

3. **Chrome Extension**:
   - Load from `/app/chrome-extension` folder

### Test the APIs

```bash
# Create a user mapping
curl -X POST http://localhost:8001/api/admin/mappings \
  -H "Content-Type: application/json" \
  -d '{
    "jobdiva_user_id": "jd_user_001",
    "jobdiva_user_name": "Alice Johnson",
    "goto_user_id": "goto_user_001",
    "goto_phone_number": "+14155551001"
  }'

# Send an SMS
curl -X POST http://localhost:8001/api/sms/send \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_id": "cand_12345",
    "candidate_name": "John Doe",
    "candidate_phone": "+14155552671",
    "recruiter_id": "jd_user_001",
    "recruiter_name": "Alice Johnson",
    "message": "Hi John, exciting opportunity to discuss!"
  }'

# View interaction logs
curl http://localhost:8001/api/admin/logs
```

## 📁 Project Structure

```
/app/
├── backend/                      # FastAPI Backend
│   ├── server.py                 # Main application
│   ├── models/                   # Pydantic models
│   ├── routes/                   # API endpoints
│   ├── services/                 # External API integrations (MOCKED)
│   └── utils/                    # Utilities (phone normalization)
│
├── frontend/                     # React Frontend
│   ├── src/
│   │   ├── pages/AdminPage.js    # Admin dashboard
│   │   └── components/           # React components
│   └── package.json
│
├── chrome-extension/             # Chrome Extension
│   ├── manifest.json             # Extension config
│   ├── content.js                # Runs on JobDiva pages
│   ├── background.js             # Service worker
│   ├── popup.html                # Configuration UI
│   └── README.md                 # Extension docs
│
├── IMPLEMENTATION_GUIDE.md       # Detailed implementation guide
└── README.md                     # This file
```

## 🔑 Key Features

### Backend Features
- ✅ SMS sending with candidate note creation
- ✅ Call initiation with logging
- ✅ Webhook handlers for GoTo events
- ✅ User mapping management (CRUD)
- ✅ Interaction history tracking
- ✅ Phone number normalization (E.164)
- ✅ Comprehensive error handling

### Admin Dashboard Features
- ✅ Create/view/delete user mappings
- ✅ View all interactions (calls & SMS)
- ✅ Filter by type (all/SMS/calls)
- ✅ Real-time data from backend
- ✅ Responsive design

### Chrome Extension Features
- ✅ Auto-detects candidate pages
- ✅ Injects Call and SMS buttons
- ✅ SMS modal with character counter
- ✅ Configuration popup
- ✅ Automatic candidate info extraction
- ✅ Success/error notifications

## ⚠️ Current Status

### What's Working
Everything is functional with **mocked APIs**:
- All backend endpoints operational
- Admin dashboard fully interactive
- Chrome extension ready to use
- Database operations working
- Phone normalization working
- Interaction logging working

### What Needs Real Implementation

Two service files need real API integration:

1. **`/app/backend/services/goto_service.py`**
   - Replace mocked OAuth2 authentication
   - Replace mocked SMS sending
   - Replace mocked call initiation
   - Add real webhook signature verification

2. **`/app/backend/services/jobdiva_service.py`**
   - Replace mocked authentication
   - Replace mocked candidate note creation
   - Replace mocked candidate search

**See `IMPLEMENTATION_GUIDE.md` for detailed instructions on replacing mocked APIs.**

## 📝 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/` | API health and info |
| POST | `/api/sms/send` | Send SMS via GoTo |
| POST | `/api/call/start` | Initiate call via GoTo |
| POST | `/api/webhooks/goto/messages` | Handle SMS webhooks |
| POST | `/api/webhooks/goto/call-events` | Handle call webhooks |

### Admin Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/mappings` | List all user mappings |
| POST | `/api/admin/mappings` | Create user mapping |
| GET | `/api/admin/mappings/{id}` | Get specific mapping |
| PUT | `/api/admin/mappings/{id}` | Update mapping |
| DELETE | `/api/admin/mappings/{id}` | Delete mapping |
| GET | `/api/admin/logs` | List interaction logs |
| GET | `/api/admin/logs/{id}` | Get specific log |

## 🔧 Configuration

### Backend Environment Variables
Located in `/app/backend/.env`:
```
MONGO_URL=mongodb://localhost:27017
DB_NAME=test_database
CORS_ORIGINS=*

# Add these when you have real credentials:
# GOTO_CLIENT_ID=your_client_id
# GOTO_CLIENT_SECRET=your_client_secret
# JOBDIVA_API_KEY=your_api_key
# JOBDIVA_BASE_URL=https://api.jobdiva.com
```

### Frontend Environment Variables
Located in `/app/frontend/.env`:
```
REACT_APP_BACKEND_URL=https://recruiter-bridge.preview.emergentagent.com
```

### Chrome Extension Configuration
Configure in extension popup:
- Backend API URL
- JobDiva User ID (optional)
- Recruiter Name

## 📚 Documentation

- **`IMPLEMENTATION_GUIDE.md`** - Comprehensive implementation guide with real API integration instructions
- **`/app/chrome-extension/README.md`** - Chrome extension documentation
- **API Docs** - http://localhost:8001/docs (Swagger UI)

## 🛠️ Technology Stack

- **Backend**: Python 3.x, FastAPI, Motor (MongoDB async)
- **Frontend**: React 19, TailwindCSS, Axios
- **Database**: MongoDB
- **Extension**: JavaScript (ES6+), Chrome Extension Manifest v3
- **External APIs**: GoTo Connect (mocked), JobDiva (mocked)

## 📋 Next Steps

1. **Get API Credentials**
   - Register for GoTo Connect developer account
   - Get JobDiva API access

2. **Implement Real APIs**
   - Follow `IMPLEMENTATION_GUIDE.md`
   - Replace mocked functions in service files
   - Test each integration individually

3. **Customize Chrome Extension**
   - Adjust selectors for your JobDiva layout
   - Test on real JobDiva pages
   - Update backend URL to deployed version

4. **Deploy to Production**
   - Deploy backend and frontend (Emergent or AWS)
   - Update extension with production URLs
   - Submit extension to Chrome Web Store

---

**Version**: 1.0.0  
**Status**: ✅ Fully functional with mocked APIs - Ready for real API integration
