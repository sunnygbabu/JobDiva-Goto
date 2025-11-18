# Chrome Extension Testing Guide

## Installation

1. **Open Chrome Browser**

2. **Go to Extensions Page**:
   - Type in address bar: `chrome://extensions/`
   - OR click Menu (⋮) → More Tools → Extensions

3. **Enable Developer Mode**:
   - Look for "Developer mode" toggle in top-right corner
   - Turn it ON

4. **Load Extension**:
   - Click "Load unpacked" button
   - Navigate to: `/app/chrome-extension`
   - Click "Select Folder"

5. **Verify Installation**:
   - You should see "JobDiva-GoTo Bridge" in your extensions list
   - Note: You'll see warnings about missing icons (these are placeholders)
   - Extension icon should appear in Chrome toolbar

## Configuration

1. **Click Extension Icon** in Chrome toolbar

2. **Configure Settings**:
   - Backend API URL: `http://localhost:8001/api` (for local testing)
   - JobDiva User ID: `recruiter_001` (optional)
   - Your Name: `John Smith`

3. **Click "Save Configuration"**

4. **Verify**: You should see "Configuration saved successfully!" message

## Testing the Extension

### Option 1: Test on ANY Webpage (Quick Test)

Since JobDiva requires login, let's first test on any webpage:

1. **Open any webpage** (e.g., https://example.com)

2. **Open Browser Console**:
   - Press F12 or Right-click → Inspect
   - Go to "Console" tab

3. **Check Logs**:
   - Look for messages like: `[JobDiva-GoTo Bridge] Content script loaded`
   - The extension runs but won't show buttons (URL doesn't contain "candidate")

### Option 2: Simulate JobDiva Page (Best for Testing)

Create a test HTML page that simulates JobDiva:

1. Create test page:
```bash
cat > /tmp/test-jobdiva-page.html << 'HTML'
<!DOCTYPE html>
<html>
<head>
    <title>Test Candidate Page</title>
</head>
<body style="font-family: Arial; padding: 20px;">
    <h1>JobDiva Test - Candidate Profile</h1>
    
    <div class="candidate-header">
        <h2 data-testid="candidate-name">Jane Doe</h2>
        <p>Candidate ID: <span data-testid="candidate-id">cand_12345</span></p>
        <p>Phone: <span data-testid="candidate-phone">+1 (415) 555-9999</span></p>
        <p>Email: jane.doe@example.com</p>
    </div>
    
    <div class="candidate-details">
        <h3>Details</h3>
        <p>This is a test candidate page to demonstrate the Chrome extension.</p>
        <p>The extension should inject Call and SMS buttons above.</p>
    </div>
    
    <div style="margin-top: 20px; padding: 15px; background: #f0f0f0; border-radius: 5px;">
        <h4>Instructions:</h4>
        <ol>
            <li>Make sure the Chrome extension is installed and configured</li>
            <li>The URL must contain "candidate" for buttons to appear</li>
            <li>Look for "Call via GoTo" and "Text via GoTo" buttons above</li>
            <li>Open browser console (F12) to see extension logs</li>
        </ol>
    </div>
</body>
</html>
HTML
```

2. **Rename to include "candidate"**:
```bash
mv /tmp/test-jobdiva-page.html /tmp/test-candidate-page.html
```

3. **Open in Chrome**:
   - Drag the file into Chrome
   - OR type: `file:///tmp/test-candidate-page.html`

4. **You should see**:
   - Two buttons: "Call via GoTo" (green) and "Text via GoTo" (blue)
   - If not, check browser console for errors

5. **Test Call Button**:
   - Click "Call via GoTo"
   - Confirm the dialog
   - Check alert message: Should say "Call initiated successfully"
   - Check browser console for API call logs

6. **Test SMS Button**:
   - Click "Text via GoTo"
   - Modal should appear with message input
   - Type a test message
   - Click "Send SMS"
   - Should see success alert

7. **Verify Backend Received Requests**:
```bash
# Check interaction logs
curl http://localhost:8001/api/admin/logs | jq .
```

### Option 3: Test on Real JobDiva (If You Have Access)

1. **Log into JobDiva**

2. **Navigate to any candidate page**

3. **Look for the buttons**:
   - Should appear near candidate header
   - If not, you may need to adjust CSS selectors

4. **Adjust Selectors if Needed**:
   - Right-click on candidate name → Inspect
   - Note the class names/attributes
   - Edit `/app/chrome-extension/content.js`
   - Update the selectors in `extractCandidateInfo()` function

## Troubleshooting

### Buttons not appearing:
- Check console for errors (F12)
- Verify URL contains "candidate"
- Check if content script loaded (see console logs)
- Try refreshing the page

### API calls failing:
- Verify backend is running: `curl http://localhost:8001/api/`
- Check backend URL in extension popup
- Look for CORS errors in console
- Verify extension configuration is saved

### Cannot extract candidate info:
- Open browser console
- Check what `extractCandidateInfo()` returns
- Update selectors in content.js to match your page structure

## Success Indicators

✅ Extension appears in chrome://extensions/
✅ Can configure in popup
✅ Content script logs appear in console
✅ Buttons appear on pages with "candidate" in URL
✅ Clicking buttons shows modals/alerts
✅ API calls reach backend (check logs)
✅ Interactions appear in admin dashboard

