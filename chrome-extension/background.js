// JobDiva-GoTo Bridge Background Service Worker

console.log('[JobDiva-GoTo Bridge] Background service worker loaded');

// Listen for extension installation
chrome.runtime.onInstalled.addListener((details) => {
  console.log('[JobDiva-GoTo Bridge] Extension installed:', details.reason);
  
  if (details.reason === 'install') {
    // Set default configuration
    chrome.storage.local.set({
      backendApiUrl: 'https://recruiter-bridge.preview.emergentagent.com/api',
      recruiterInfo: null
    });
  }
});

// Listen for messages from content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('[JobDiva-GoTo Bridge] Message received:', request);
  
  if (request.action === 'getConfig') {
    chrome.storage.local.get(['backendApiUrl', 'recruiterInfo'], (result) => {
      sendResponse(result);
    });
    return true; // Keep channel open for async response
  }
  
  if (request.action === 'setConfig') {
    chrome.storage.local.set(request.config, () => {
      sendResponse({ success: true });
    });
    return true;
  }
  
  if (request.action === 'notification') {
    // Show notification
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icon48.png',
      title: request.title || 'JobDiva-GoTo Bridge',
      message: request.message
    });
    sendResponse({ success: true });
    return true;
  }
});

// Listen for tab updates (to inject content script if needed)
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.url && tab.url.includes('jobdiva.com')) {
    console.log('[JobDiva-GoTo Bridge] JobDiva page loaded:', tab.url);
  }
});
