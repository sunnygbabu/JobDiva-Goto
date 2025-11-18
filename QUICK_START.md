# 🚀 Quick Start Guide

## 5-Minute Test

### 1️⃣ Test Backend (1 min)

```bash
# Create user mapping
curl -X POST http://localhost:8001/api/admin/mappings \
  -H "Content-Type: application/json" \
  -d '{"jobdiva_user_id":"rec_001","jobdiva_user_name":"John Doe","goto_user_id":"goto_001","goto_phone_number":"+14155551234"}'

# Send test SMS
curl -X POST http://localhost:8001/api/sms/send \
  -H "Content-Type: application/json" \
  -d '{"candidate_id":"c1","candidate_name":"Jane","candidate_phone":"+14155559999","recruiter_id":"rec_001","recruiter_name":"John","message":"Test SMS"}'
```

### 2️⃣ Test Dashboard (2 min)

Open: **http://localhost:3000/admin**

- ✅ See your mapping
- ✅ See interaction log with your SMS

### 3️⃣ Test Chrome Extension (2 min)

1. **Install**:
   - `chrome://extensions/` → Developer mode ON → Load unpacked → Select `/app/chrome-extension`

2. **Configure**:
   - Click extension icon
   - Backend URL: `http://localhost:8001/api`
   - Save

3. **Test**:
   - Open: `file:///app/test-candidate-page.html`
   - You should see Call and SMS buttons
   - Click "Text via GoTo" → Type message → Send
   - Check admin dashboard for new log entry

---

## 📂 Key Locations

| Component | URL/Path |
|-----------|----------|
| Backend API | http://localhost:8001/api/ |
| API Docs | http://localhost:8001/docs |
| Admin Dashboard | http://localhost:3000/admin |
| Extension Folder | `/app/chrome-extension` |
| Test Page | `/app/test-candidate-page.html` |

---

## 🔧 Quick Commands

```bash
# Check service status
sudo supervisorctl status

# Restart backend
sudo supervisorctl restart backend

# View backend logs
tail -n 50 /var/log/supervisor/backend.err.log

# View all interaction logs
curl http://localhost:8001/api/admin/logs | jq .

# Count total interactions
curl http://localhost:8001/api/admin/logs | jq 'length'
```

---

## 🎯 What Works Right Now

✅ **Backend**: All APIs functional with mocked GoTo/JobDiva  
✅ **Dashboard**: Full user mapping & log management  
✅ **Extension**: Inject buttons on candidate pages, send SMS/calls  
✅ **Database**: MongoDB storing all interactions  
✅ **Integration**: Complete flow from extension → backend → dashboard  

---

## ⚠️ What's Mocked

❌ **GoTo Connect API**: SMS sending, call initiation, webhooks  
❌ **JobDiva API**: Candidate notes, candidate search  

**To fix**: See `IMPLEMENTATION_GUIDE.md` for replacing mocked services

---

## 📚 Full Documentation

- **README.md** - Overview and features
- **TESTING_GUIDE.md** - Comprehensive testing instructions
- **IMPLEMENTATION_GUIDE.md** - How to integrate real APIs
- **DEPLOYMENT_CHECKLIST.md** - Production deployment steps
- **chrome-extension/README.md** - Extension-specific docs

---

## 🆘 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Backend not responding | `sudo supervisorctl restart backend` |
| Dashboard not loading | Check `http://localhost:3000` is accessible |
| Extension buttons missing | URL must contain "candidate", check console (F12) |
| API calls failing | Verify backend URL in extension popup |
| CORS errors | Check `CORS_ORIGINS=*` in `/app/backend/.env` |

---

## ✉️ Test Data Examples

### Create Mapping
```json
{
  "jobdiva_user_id": "jd_001",
  "jobdiva_user_name": "Alice Smith",
  "goto_user_id": "goto_001",
  "goto_phone_number": "+14155551234"
}
```

### Send SMS
```json
{
  "candidate_id": "cand_001",
  "candidate_name": "John Doe",
  "candidate_phone": "+14155559999",
  "recruiter_id": "jd_001",
  "recruiter_name": "Alice Smith",
  "message": "Hi John! I have an exciting opportunity to discuss."
}
```

### Initiate Call
```json
{
  "candidate_id": "cand_001",
  "candidate_name": "John Doe",
  "candidate_phone": "+14155559999",
  "recruiter_id": "jd_001",
  "recruiter_name": "Alice Smith"
}
```

---

## 🎓 Next Steps

1. ✅ **Test everything** (follow TESTING_GUIDE.md)
2. 📝 **Get API credentials** (GoTo Connect, JobDiva)
3. 🔧 **Replace mocked services** (IMPLEMENTATION_GUIDE.md)
4. 🚀 **Deploy to production** (DEPLOYMENT_CHECKLIST.md)
5. 📦 **Publish extension** to Chrome Web Store

---

## 💡 Tips

- Use the test page (`/app/test-candidate-page.html`) to test extension without JobDiva access
- Check browser console (F12) for detailed logs
- Admin dashboard updates in real-time - use Refresh button
- All phone numbers are normalized to E.164 format automatically
- MongoDB collections: `user_mappings`, `interaction_logs`

---

**Version**: 1.0.0  
**Status**: ✅ Fully functional with mocked APIs  
**Ready for**: Real API integration & deployment
