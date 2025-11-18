# JobDiva-GoTo Bridge Chrome Extension

Chrome extension that integrates JobDiva ATS with GoTo Connect for seamless calling and SMS messaging.

## Features

- **Call Integration**: Initiate calls from JobDiva candidate pages through GoTo Connect
- **SMS Messaging**: Send SMS messages to candidates with full tracking
- **Automatic Note Creation**: Creates journal notes in JobDiva for all interactions
- **Easy Configuration**: Simple popup interface for setting up backend API and recruiter info

## Installation

### For Development/Testing:

1. **Clone or download** this extension folder

2. **Open Chrome** and navigate to `chrome://extensions/`

3. **Enable Developer Mode** (toggle in top right)

4. **Click "Load unpacked"** and select the `chrome-extension` folder

5. **Configure the extension**:
   - Click the extension icon in Chrome toolbar
   - Enter your backend API URL (default: https://recruiter-bridge.preview.emergentagent.com/api)
   - Enter your JobDiva User ID and Name
   - Click "Save Configuration"

### For Production (Chrome Web Store):

1. **Add icons** (required for Chrome Web Store):
   - Create `icon16.png` (16x16)
   - Create `icon48.png` (48x48)
   - Create `icon128.png` (128x128)

2. **Package the extension**:
   ```bash
   zip -r jobdiva-goto-bridge.zip * -x "*.DS_Store" -x "README.md"
   ```

3. **Submit to Chrome Web Store**:
   - Go to [Chrome Web Store Developer Dashboard](https://chrome.google.com/webstore/devconsole)
   - Pay one-time $5 developer fee (if first time)
   - Upload the ZIP file
   - Fill in store listing details:
     - Name: JobDiva-GoTo Bridge
     - Description: (See below)
     - Screenshots: (Capture from usage)
     - Privacy policy: (Create one)
   - Submit for review (typically 1-3 days)

## Usage

1. **Navigate to a candidate page** in JobDiva (URL should contain "candidate")

2. **Look for the bridge buttons** at the top of the candidate details:
   - **Call via GoTo**: Click to initiate a call
   - **Text via GoTo**: Click to send an SMS

3. **For SMS**:
   - A modal will appear
   - Enter your message (max 1000 characters)
   - Click "Send SMS"

4. **View interaction history**:
   - Open the Admin Dashboard (link in extension popup)
   - See all calls and SMS with full details

## Configuration

### Backend API URL
The extension needs to communicate with your deployed bridge service backend. Update this in the extension popup.

**Default**: `https://recruiter-bridge.preview.emergentagent.com/api`

### Recruiter Information
Set your JobDiva User ID and name so interactions are properly attributed to you.

## Customization

### Adjusting for Your JobDiva Layout

The extension uses CSS selectors to find candidate information on JobDiva pages. You may need to adjust these in `content.js`:

```javascript
// In extractCandidateInfo() function
const candidateNameElement = document.querySelector('[your-actual-selector]');
const candidatePhoneElement = document.querySelector('[your-actual-selector]');
```

**How to find the right selectors**:
1. Open a candidate page in JobDiva
2. Right-click on the candidate name → Inspect
3. Note the class names or data attributes
4. Update the selectors in `content.js`

### Changing Button Position

By default, buttons try to insert at the top of candidate details. To change:

```javascript
// In createActionButtons() function
const insertionPoint = document.querySelector('[your-preferred-location]');
```

## API Endpoints Used

The extension communicates with these backend endpoints:

- `POST /api/call/start` - Initiate a call
- `POST /api/sms/send` - Send an SMS

## Troubleshooting

### Buttons not appearing
- Check browser console for errors (F12 → Console)
- Verify you're on a candidate page
- Check if content script is loading (you should see log messages)

### API calls failing
- Verify backend API URL in extension settings
- Check backend is running and accessible
- Look for CORS errors in console

### Phone number not detected
- Inspect the page to find the correct selector for phone numbers
- Update `extractCandidateInfo()` in `content.js`

## Privacy & Permissions

This extension requires:
- **activeTab**: To read candidate information from JobDiva pages
- **storage**: To save your configuration settings
- **host_permissions** for `*.jobdiva.com`: To inject the bridge functionality

**No data is collected or shared**. All interactions go directly to your configured backend API.

## Support

For issues or questions:
1. Check the Admin Dashboard logs
2. Review browser console for errors
3. Verify backend API is operational

## Version History

**v1.0.0** (Initial Release)
- Call initiation from JobDiva
- SMS messaging with modal interface
- Automatic JobDiva note creation
- Configuration popup
- Interaction logging
