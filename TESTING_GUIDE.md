# Complete Testing Guide - JobDiva-GoTo Bridge

## 🎯 Quick Start Testing (15 minutes)

Follow these steps in order to test all components:

---

## ✅ Phase 1: Backend API Testing (5 min)

### Step 1.1: Verify Backend is Running

```bash
curl http://localhost:8001/api/
```

**Expected Output**:
```json
{
  "message": "JobDiva-GoTo Bridge API",
  "version": "1.0.0",
  "status": "operational",
  "endpoints": { ... }
}
```

### Step 1.2: Create Test User Mapping

```bash
curl -X POST http://localhost:8001/api/admin/mappings \
  -H "Content-Type: application/json" \
  -d '{
    "jobdiva_user_id": "test_recruiter_001",
    "jobdiva_user_name": "Test Recruiter",
    "goto_user_id": "goto_test_001",
    "goto_phone_number": "+14155551234"
  }'
```

**Expected**: Returns mapping with `"is_active": true`

### Step 1.3: Test SMS Sending

```bash
curl -X POST http://localhost:8001/api/sms/send \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_id": "test_cand_001",
    "candidate_name": "Test Candidate",
    "candidate_phone": "+14155559999",
    "recruiter_id": "test_recruiter_001",
    "recruiter_name": "Test Recruiter",
    "message": "This is a test SMS from the bridge service!"
  }'
```

**Expected**: `"success": true` and `"jobdiva_note_created": true`

### Step 1.4: Test Call Initiation

```bash
curl -X POST http://localhost:8001/api/call/start \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_id": "test_cand_001",
    "candidate_name": "Test Candidate",
    "candidate_phone": "+14155559999",
    "recruiter_id": "test_recruiter_001",
    "recruiter_name": "Test Recruiter"
  }'
```

**Expected**: `"success": true` and `"call_method": "api"`

### Step 1.5: View Interaction Logs

```bash
curl http://localhost:8001/api/admin/logs
```

**Expected**: Array with 2 interactions (1 SMS, 1 call)

### ✅ Backend Test Complete!

All endpoints working? Move to Phase 2.

---

## ✅ Phase 2: Admin Dashboard Testing (5 min)

### Step 2.1: Open Admin Dashboard

Open your browser and navigate to:
```
http://localhost:3000/admin
```

### Step 2.2: Test User Mappings

1. **View Existing Mappings**:
   - You should see the mapping created in Phase 1
   - Verify: Test Recruiter / +14155551234

2. **Create New Mapping**:
   - Click "Add New Mapping" button
   - Fill in:
     - JobDiva User ID: `recruiter_002`
     - JobDiva User Name: `Alice Johnson`
     - GoTo User ID: `goto_002`
     - GoTo Phone: `+14155555678`
   - Click "Create Mapping"
   - **Expected**: Green success message, mapping appears in table

3. **Test Deactivate**:
   - Click "Deactivate" on any mapping
   - Confirm dialog
   - **Expected**: Mapping status changes to "Inactive"

### Step 2.3: Test Interaction Logs

1. **View All Logs**:
   - Scroll to "Interaction Logs" section
   - You should see interactions from Phase 1

2. **Test Filters**:
   - Click "SMS" button → Should show only SMS
   - Click "Calls" button → Should show only calls
   - Click "All" button → Should show everything

3. **Check Log Details**:
   - Each log should show:
     - Type badge (SMS/CALL)
     - Direction (INBOUND/OUTBOUND)
     - Status (SENT/COMPLETED)
     - Recruiter and Candidate info
     - Timestamp
     - JobDiva Note status

### ✅ Dashboard Test Complete!

Everything working? Move to Phase 3.

---

## ✅ Phase 3: Chrome Extension Testing (10 min)

### Step 3.1: Install Extension

1. **Open Chrome** and go to: `chrome://extensions/`

2. **Enable Developer Mode**:
   - Toggle "Developer mode" in top-right corner

3. **Load Extension**:
   - Click "Load unpacked"
   - Navigate to: `/app/chrome-extension`
   - Click "Select Folder"

4. **Verify**:
   - "JobDiva-GoTo Bridge" appears in list
   - Extension icon in Chrome toolbar
   - ⚠️ Ignore warnings about missing icons (placeholders)

### Step 3.2: Configure Extension

1. **Click extension icon** in toolbar

2. **Configure**:
   - Backend API URL: `http://localhost:8001/api`
   - JobDiva User ID: `test_recruiter_001`
   - Your Name: `Test Recruiter`

3. **Save Configuration**

4. **Expected**: "Configuration saved successfully!" message

### Step 3.3: Test on Simulator Page

1. **Open test page** in Chrome:
   ```
   file:///app/test-candidate-page.html
   ```
   Or drag `/app/test-candidate-page.html` into Chrome

2. **Open Browser Console** (F12 or Cmd+Option+J)

3. **Check Console Logs**:
   Look for:
   ```
   [JobDiva-GoTo Bridge] Content script loaded
   [JobDiva-GoTo Bridge] Candidate page detected, initializing...
   ```

4. **Verify Buttons Appear**:
   - Look for two buttons at top of candidate info
   - 🟢 "Call via GoTo" (green)
   - 🔵 "Text via GoTo" (blue)

### Step 3.4: Test Call Feature

1. **Click "Call via GoTo"** button

2. **Confirm dialog**: "Initiate call to Test Candidate at +14155559999?"

3. **Expected Results**:
   - Alert: "Call initiated successfully! JobDiva note: Created"
   - Console shows API call
   - No errors in console

4. **Verify in Backend**:
   ```bash
   curl http://localhost:8001/api/admin/logs | jq 'length'
   ```
   Should show +1 more interaction

### Step 3.5: Test SMS Feature

1. **Click "Text via GoTo"** button

2. **Modal should appear** with:
   - To: Test Candidate (+14155559999)
   - From: Test Recruiter
   - Message textarea
   - Character counter

3. **Type test message**:
   ```
   Hi! This is a test SMS from the Chrome extension integration.
   ```

4. **Click "Send SMS"**

5. **Expected Results**:
   - Alert: "SMS sent successfully! JobDiva note: Created"
   - Modal closes
   - Console shows API call
   - No errors

6. **Verify in Admin Dashboard**:
   - Open: http://localhost:3000/admin
   - Scroll to Interaction Logs
   - Click "Refresh"
   - Should see new SMS entry with your message

### Step 3.6: Test Different Scenarios

1. **Test without phone number**:
   - Modify test page HTML to remove phone
   - Refresh page
   - Click "Call via GoTo"
   - **Expected**: Error alert about missing phone

2. **Test with backend offline**:
   - Stop backend: `sudo supervisorctl stop backend`
   - Try to send SMS
   - **Expected**: Error alert with fetch failure
   - Restart: `sudo supervisorctl start backend`

### ✅ Extension Test Complete!

---

## 📊 Full Integration Test

Test the complete flow from extension → backend → admin dashboard:

1. **In Chrome Extension** (on test page):
   - Send SMS: "Hello from integration test!"
   - Initiate call

2. **Check Backend Logs**:
   ```bash
   tail -n 50 /var/log/supervisor/backend.*.log
   ```
   Should see API requests logged

3. **In Admin Dashboard**:
   - Refresh logs
   - Verify both interactions appear
   - Check all details are correct

4. **Verify Database**:
   ```bash
   # Check MongoDB directly
   mongosh test_database --eval "db.interaction_logs.find().pretty()"
   ```

---

## 🐛 Troubleshooting

### Backend Issues

**Problem**: Backend not responding
```bash
# Check status
sudo supervisorctl status backend

# Check logs
tail -n 100 /var/log/supervisor/backend.err.log

# Restart
sudo supervisorctl restart backend
```

**Problem**: MongoDB connection error
```bash
# Check MongoDB
sudo supervisorctl status mongodb

# Test connection
mongosh test_database --eval "db.stats()"
```

### Frontend Issues

**Problem**: Admin dashboard not loading
```bash
# Check frontend status
sudo supervisorctl status frontend

# Check logs
tail -n 100 /var/log/supervisor/frontend.err.log
```

**Problem**: API calls failing (CORS)
- Check browser console for CORS errors
- Verify `CORS_ORIGINS=*` in `/app/backend/.env`
- Restart backend after changing .env

### Extension Issues

**Problem**: Buttons not appearing
- Open console (F12) and check for errors
- Verify URL contains "candidate"
- Check: `[JobDiva-GoTo Bridge] Content script loaded` in console
- Try refreshing the page

**Problem**: API calls failing
- Verify backend URL in extension popup
- Check backend is accessible: `curl http://localhost:8001/api/`
- Look for CORS errors in console
- Try re-saving extension configuration

**Problem**: Cannot extract candidate info
- Open console and check extracted data
- Update selectors in `/app/chrome-extension/content.js`
- Look for `extractCandidateInfo()` function

---

## ✅ Testing Checklist

### Backend
- [ ] API health check returns 200
- [ ] Can create user mappings
- [ ] Can send SMS (mocked)
- [ ] Can initiate calls (mocked)
- [ ] Webhook endpoints respond
- [ ] Interaction logs created correctly
- [ ] All CRUD operations work for mappings

### Admin Dashboard
- [ ] Dashboard loads without errors
- [ ] Can view user mappings
- [ ] Can create new mappings
- [ ] Can deactivate mappings
- [ ] Interaction logs display correctly
- [ ] Filters work (All/SMS/Calls)
- [ ] Refresh updates data

### Chrome Extension
- [ ] Extension installs without critical errors
- [ ] Can configure in popup
- [ ] Configuration saves successfully
- [ ] Content script loads on candidate pages
- [ ] Buttons appear on test page
- [ ] Call button works
- [ ] SMS modal opens
- [ ] SMS can be sent
- [ ] Success/error alerts appear
- [ ] API calls reach backend
- [ ] Data appears in admin dashboard

### Integration
- [ ] Extension → Backend → Dashboard flow works
- [ ] All interactions logged in database
- [ ] Phone numbers normalized correctly
- [ ] JobDiva notes marked as created
- [ ] Timestamps correct
- [ ] Error handling works

---

## 📈 Performance Testing (Optional)

Test with multiple interactions:

```bash
# Send 10 SMS messages
for i in {1..10}; do
  curl -X POST http://localhost:8001/api/sms/send \
    -H "Content-Type: application/json" \
    -d "{
      \"candidate_id\": \"cand_$i\",
      \"candidate_name\": \"Candidate $i\",
      \"candidate_phone\": \"+1415555$i$i$i$i\",
      \"recruiter_id\": \"rec_001\",
      \"recruiter_name\": \"Test Recruiter\",
      \"message\": \"Test message $i\"
    }"
done

# Check all were logged
curl http://localhost:8001/api/admin/logs | jq 'length'
```

---

## 🎉 Success Criteria

You've successfully tested everything when:

1. ✅ All backend endpoints return successful responses
2. ✅ Admin dashboard shows live data
3. ✅ Chrome extension buttons appear and function
4. ✅ End-to-end flow works (extension → backend → dashboard)
5. ✅ Interaction logs show all test actions
6. ✅ No critical errors in any console/log

---

## 📝 Test Results Template

Record your test results:

```
DATE: [Your date]
TESTER: [Your name]

BACKEND TESTS:
[ ] API health: PASS / FAIL
[ ] Create mapping: PASS / FAIL
[ ] Send SMS: PASS / FAIL
[ ] Initiate call: PASS / FAIL
[ ] View logs: PASS / FAIL

DASHBOARD TESTS:
[ ] Load dashboard: PASS / FAIL
[ ] Create mapping: PASS / FAIL
[ ] View logs: PASS / FAIL
[ ] Filter logs: PASS / FAIL

EXTENSION TESTS:
[ ] Install: PASS / FAIL
[ ] Configure: PASS / FAIL
[ ] Buttons appear: PASS / FAIL
[ ] Call feature: PASS / FAIL
[ ] SMS feature: PASS / FAIL

INTEGRATION TEST:
[ ] Full flow: PASS / FAIL

ISSUES FOUND:
[List any issues]

NOTES:
[Any additional observations]
```

---

## 🚀 Ready for Production?

After successful testing with mocked APIs:

1. **Get real API credentials** (GoTo Connect, JobDiva)
2. **Follow IMPLEMENTATION_GUIDE.md** to replace mocked services
3. **Retest with real APIs**
4. **Deploy to production**

See `DEPLOYMENT_CHECKLIST.md` for deployment steps.
