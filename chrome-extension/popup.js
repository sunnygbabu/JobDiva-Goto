// Popup script for JobDiva-GoTo Bridge extension

document.addEventListener('DOMContentLoaded', () => {
  const backendUrlInput = document.getElementById('backend-url');
  const recruiterIdInput = document.getElementById('recruiter-id');
  const recruiterNameInput = document.getElementById('recruiter-name');
  const saveBtn = document.getElementById('save-btn');
  const statusMessage = document.getElementById('status-message');

  // Load saved configuration
  chrome.storage.local.get(['backendApiUrl', 'recruiterInfo'], (result) => {
    if (result.backendApiUrl) {
      backendUrlInput.value = result.backendApiUrl;
    }
    if (result.recruiterInfo) {
      recruiterIdInput.value = result.recruiterInfo.recruiter_id || '';
      recruiterNameInput.value = result.recruiterInfo.recruiter_name || '';
    }
  });

  // Save configuration
  saveBtn.addEventListener('click', () => {
    const config = {
      backendApiUrl: backendUrlInput.value.trim(),
      recruiterInfo: {
        recruiter_id: recruiterIdInput.value.trim() || null,
        recruiter_name: recruiterNameInput.value.trim()
      }
    };

    // Validate
    if (!config.backendApiUrl) {
      showStatus('error', 'Backend API URL is required');
      return;
    }

    if (!config.recruiterInfo.recruiter_name) {
      showStatus('error', 'Recruiter name is required');
      return;
    }

    // Save to storage
    chrome.storage.local.set(config, () => {
      showStatus('success', 'Configuration saved successfully!');
      
      // Also store in localStorage for content script access
      localStorage.setItem('jobdiva_goto_recruiter', JSON.stringify(config.recruiterInfo));
    });
  });

  // Show status message
  function showStatus(type, message) {
    const className = type === 'success' ? 'status-success' : 'status-error';
    statusMessage.innerHTML = `<div class="status ${className}">${message}</div>`;
    
    setTimeout(() => {
      statusMessage.innerHTML = '';
    }, 3000);
  }
});
