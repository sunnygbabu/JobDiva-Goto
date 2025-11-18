# Deployment Checklist

## Pre-Deployment Checklist

### ✅ Already Completed

- [x] Backend API fully implemented with all endpoints
- [x] Admin Dashboard UI complete
- [x] Chrome Extension developed
- [x] Database models and collections defined
- [x] Phone number normalization implemented
- [x] Interaction logging system working
- [x] Error handling implemented
- [x] API documentation available (Swagger)

### 🔄 Before Production Deployment

#### 1. API Integration (Critical)

**GoTo Connect** (`/app/backend/services/goto_service.py`):
- [ ] Obtain GoTo Connect API credentials (Client ID, Client Secret)
- [ ] Replace mocked `authenticate()` function
- [ ] Replace mocked `send_sms()` function
- [ ] Replace mocked `initiate_call()` function
- [ ] Add real `get_call_events()` implementation
- [ ] Test each function individually
- [ ] Add error handling for API failures

**JobDiva** (`/app/backend/services/jobdiva_service.py`):
- [ ] Obtain JobDiva API credentials and documentation
- [ ] Replace mocked `authenticate()` function
- [ ] Replace mocked `create_candidate_note()` function
- [ ] Replace mocked `find_candidate_by_phone()` function
- [ ] Test each function individually
- [ ] Verify note format matches JobDiva requirements

#### 2. Environment Configuration

**Backend** (`/app/backend/.env`):
- [ ] Add GOTO_CLIENT_ID
- [ ] Add GOTO_CLIENT_SECRET
- [ ] Add JOBDIVA_API_KEY
- [ ] Add JOBDIVA_BASE_URL
- [ ] Update CORS_ORIGINS to specific domains (not *)
- [ ] Configure production MONGO_URL (e.g., MongoDB Atlas)

**Frontend** (`/app/frontend/.env`):
- [ ] Update REACT_APP_BACKEND_URL to production URL
- [ ] Verify all environment variables are set

#### 3. Security Hardening

- [ ] Add authentication to admin endpoints
- [ ] Implement rate limiting on API endpoints
- [ ] Add webhook signature verification (GoTo Connect)
- [ ] Restrict CORS to known origins only
- [ ] Enable HTTPS for all production endpoints
- [ ] Review and sanitize all user inputs
- [ ] Add API key rotation mechanism

#### 4. Chrome Extension Customization

**Critical**:
- [ ] Test on actual JobDiva candidate pages
- [ ] Adjust CSS selectors in `content.js` for candidate info extraction
- [ ] Update BACKEND_API_URL to production endpoint
- [ ] Create proper extension icons (16x16, 48x48, 128x128)
- [ ] Write privacy policy for Chrome Web Store
- [ ] Test extension on multiple JobDiva pages

**Files to Update**:
- `/app/chrome-extension/content.js` - Update selectors and API URL
- `/app/chrome-extension/popup.html` - Update default backend URL
- Create icons: `icon16.png`, `icon48.png`, `icon128.png`

#### 5. Database Setup

**Production Database**:
- [ ] Set up MongoDB Atlas or production MongoDB instance
- [ ] Create database and collections
- [ ] Set up indexes for performance:
  - `user_mappings`: Index on `jobdiva_user_id`, `goto_phone_number`
  - `interaction_logs`: Index on `candidate_id`, `timestamp`
- [ ] Configure backup strategy
- [ ] Set up monitoring and alerts

#### 6. Testing

**Backend**:
- [ ] Test all API endpoints with real credentials
- [ ] Test webhook handlers with real GoTo events
- [ ] Load test critical endpoints
- [ ] Test error scenarios (API failures, invalid data)
- [ ] Verify all JobDiva notes are created correctly

**Frontend**:
- [ ] Test user mapping CRUD operations
- [ ] Test interaction log filtering and display
- [ ] Test on different browsers
- [ ] Test responsive design on mobile

**Chrome Extension**:
- [ ] Test on real JobDiva pages
- [ ] Test call initiation flow
- [ ] Test SMS sending flow
- [ ] Test error handling
- [ ] Verify candidate info extraction accuracy

## Deployment Steps

### Option 1: Emergent Platform

#### Web Application (Backend + Frontend)
1. [ ] Commit all changes to Git
2. [ ] Click "Deploy" in Emergent dashboard
3. [ ] Wait for deployment to complete
4. [ ] Verify deployment URL
5. [ ] Test all endpoints on deployed instance
6. [ ] Monitor logs for any errors

**Cost**: 50 credits/month

#### Chrome Extension
1. [ ] Update backend URL in extension to deployed URL
2. [ ] Test extension with deployed backend
3. [ ] Follow Chrome Web Store submission (see below)

### Option 2: AWS Deployment

#### Backend (FastAPI)

**Option A: Elastic Beanstalk**
1. [ ] Install AWS CLI and EB CLI
2. [ ] Initialize Elastic Beanstalk: `eb init`
3. [ ] Create environment: `eb create production`
4. [ ] Set environment variables
5. [ ] Deploy: `eb deploy`
6. [ ] Verify deployment: `eb status`

**Option B: AWS Lambda + API Gateway**
1. [ ] Install Mangum for Lambda compatibility
2. [ ] Package application with dependencies
3. [ ] Create Lambda function
4. [ ] Set up API Gateway
5. [ ] Configure environment variables
6. [ ] Test endpoints

**Option C: EC2**
1. [ ] Launch EC2 instance (Ubuntu/Amazon Linux)
2. [ ] SSH into instance
3. [ ] Clone repository
4. [ ] Install dependencies
5. [ ] Set up systemd service or PM2
6. [ ] Configure nginx reverse proxy
7. [ ] Enable HTTPS with Let's Encrypt

#### Frontend (React)

**Option A: S3 + CloudFront**
1. [ ] Build frontend: `yarn build`
2. [ ] Create S3 bucket
3. [ ] Enable static website hosting
4. [ ] Upload build files to S3
5. [ ] Create CloudFront distribution
6. [ ] Configure custom domain (optional)
7. [ ] Enable HTTPS

**Option B: Serve from FastAPI**
1. [ ] Build frontend: `yarn build`
2. [ ] Copy build to backend static folder
3. [ ] Configure FastAPI to serve static files
4. [ ] Deploy backend (includes frontend)

#### Database

**MongoDB Atlas** (Recommended):
1. [ ] Create MongoDB Atlas account
2. [ ] Create cluster
3. [ ] Configure network access (whitelist IPs)
4. [ ] Create database user
5. [ ] Get connection string
6. [ ] Update MONGO_URL in backend .env
7. [ ] Test connection

### Chrome Web Store Submission

1. **Prepare Extension**:
   - [ ] Update manifest.json version
   - [ ] Create high-quality icons (16x16, 48x48, 128x128)
   - [ ] Write detailed description
   - [ ] Take screenshots (1280x800 or 640x400)
   - [ ] Create promotional images (optional)

2. **Create Privacy Policy**:
   - [ ] Document data collection (if any)
   - [ ] Explain API communications
   - [ ] Host privacy policy on public URL

3. **Package Extension**:
   ```bash
   cd /app/chrome-extension
   zip -r jobdiva-goto-bridge.zip * -x "*.DS_Store" -x "README.md" -x "*.sh"
   ```

4. **Submit to Chrome Web Store**:
   - [ ] Go to [Chrome Web Store Developer Dashboard](https://chrome.google.com/webstore/devconsole)
   - [ ] Pay $5 one-time developer registration fee
   - [ ] Click "New Item"
   - [ ] Upload ZIP file
   - [ ] Fill in store listing:
     - Name: JobDiva-GoTo Bridge
     - Summary: (50 characters)
     - Description: (See example below)
     - Category: Productivity
     - Language: English
   - [ ] Upload screenshots
   - [ ] Add privacy policy URL
   - [ ] Select visibility (Public/Unlisted/Private)
   - [ ] Submit for review

5. **Wait for Review**:
   - Typically takes 1-3 days
   - You'll receive email when approved
   - Address any feedback if rejected

**Store Description Example**:
```
Seamless integration between JobDiva ATS and GoTo Connect.

Features:
• Initiate calls to candidates directly from JobDiva pages
• Send SMS messages with automatic tracking
• Automatic journal note creation in JobDiva
• Complete interaction history
• Easy configuration and setup

This extension requires:
- Access to JobDiva ATS
- GoTo Connect account
- Backend bridge service (provided separately)

For setup instructions and support, visit [your-website.com]
```

## Post-Deployment

### Monitoring & Maintenance

- [ ] Set up application monitoring (errors, performance)
- [ ] Configure log aggregation
- [ ] Set up uptime monitoring
- [ ] Create alerts for critical errors
- [ ] Monitor API rate limits
- [ ] Track database performance

### Documentation

- [ ] Update README with production URLs
- [ ] Document any configuration changes
- [ ] Create runbook for common issues
- [ ] Document API integration process
- [ ] Create user guide for recruiters

### User Onboarding

- [ ] Create setup guide for recruiters
- [ ] Document how to install Chrome extension
- [ ] Provide training on using the bridge service
- [ ] Set up support channel (email/Slack)
- [ ] Create FAQ document

## Rollback Plan

If issues occur after deployment:

### Backend Rollback
- [ ] Keep previous version tagged in Git
- [ ] Document rollback procedure
- [ ] Test rollback process in staging

### Extension Rollback
- [ ] Chrome Web Store allows reverting to previous version
- [ ] Keep old version ZIP files
- [ ] Notify users if critical update needed

## Success Metrics

Track these after deployment:

- [ ] API response times
- [ ] Error rates
- [ ] Number of successful SMS/call interactions
- [ ] JobDiva note creation success rate
- [ ] Extension installation count
- [ ] User feedback and ratings

## Support Resources

- **Backend Issues**: Check logs at `/var/log/supervisor/backend.*.log`
- **Frontend Issues**: Check browser console
- **Extension Issues**: Check browser console on JobDiva pages
- **API Docs**: `https://your-domain.com/docs`
- **Implementation Guide**: `/app/IMPLEMENTATION_GUIDE.md`

---

## Quick Reference

### Testing URLs (Local)
- Backend: http://localhost:8001
- API Docs: http://localhost:8001/docs
- Frontend: http://localhost:3000
- Admin: http://localhost:3000/admin

### Production URLs (Update these)
- Backend: [Your production backend URL]
- Frontend: [Your production frontend URL]
- Admin Dashboard: [Your admin dashboard URL]

### Key Files to Update for Production
1. `/app/backend/.env` - Add real API credentials
2. `/app/backend/services/goto_service.py` - Replace mocked functions
3. `/app/backend/services/jobdiva_service.py` - Replace mocked functions
4. `/app/frontend/.env` - Update backend URL
5. `/app/chrome-extension/content.js` - Update API URL and selectors
6. `/app/chrome-extension/popup.html` - Update default backend URL

---

**Last Updated**: January 2025
**Version**: 1.0.0
