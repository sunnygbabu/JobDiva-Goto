// JobDiva-GoTo Bridge Content Script
// Runs on JobDiva candidate pages

(function() {
  'use strict';

  // Configuration - Update this with your deployed backend URL
  const BACKEND_API_URL = 'https://recruiter-bridge.preview.emergentagent.com/api';

  // State
  let currentCandidate = null;
  let currentRecruiter = null;

  console.log('[JobDiva-GoTo Bridge] Content script loaded');

  // Extract candidate information from the JobDiva page
  function extractCandidateInfo() {
    // NOTE: These selectors are examples and will need to be adjusted
    // based on actual JobDiva page structure
    
    try {
      // Example selectors - adjust based on real JobDiva page structure
      const candidateNameElement = document.querySelector('[data-testid="candidate-name"]') || 
                                     document.querySelector('.candidate-name') ||
                                     document.querySelector('h1.candidate-header');
      
      const candidatePhoneElement = document.querySelector('[data-testid="candidate-phone"]') ||
                                     document.querySelector('.candidate-phone') ||
                                     document.querySelector('a[href^="tel:"]');
      
      const candidateIdElement = document.querySelector('[data-testid="candidate-id"]') ||
                                  document.querySelector('.candidate-id');

      // Extract text content
      const candidateName = candidateNameElement ? candidateNameElement.textContent.trim() : 'Unknown Candidate';
      const candidatePhone = candidatePhoneElement ? 
                              candidatePhoneElement.textContent.trim().replace(/[^0-9+]/g, '') : 
                              null;
      const candidateId = candidateIdElement ? candidateIdElement.textContent.trim() : null;

      // If we can't find phone, try URL params or other sources
      const urlParams = new URLSearchParams(window.location.search);
      const candidateIdFromUrl = urlParams.get('candidateId') || urlParams.get('id');

      return {
        candidate_id: candidateId || candidateIdFromUrl,
        candidate_name: candidateName,
        candidate_phone: candidatePhone
      };
    } catch (error) {
      console.error('[JobDiva-GoTo Bridge] Error extracting candidate info:', error);
      return null;
    }
  }

  // Extract recruiter/user information
  function extractRecruiterInfo() {
    try {
      // Get from localStorage if available
      const storedRecruiter = localStorage.getItem('jobdiva_goto_recruiter');
      if (storedRecruiter) {
        return JSON.parse(storedRecruiter);
      }

      // Try to extract from page
      const userNameElement = document.querySelector('.user-name') ||
                               document.querySelector('[data-testid="user-name"]');
      
      const recruiterName = userNameElement ? userNameElement.textContent.trim() : 'Unknown Recruiter';

      return {
        recruiter_id: null,
        recruiter_name: recruiterName
      };
    } catch (error) {
      console.error('[JobDiva-GoTo Bridge] Error extracting recruiter info:', error);
      return {
        recruiter_id: null,
        recruiter_name: 'Unknown Recruiter'
      };
    }
  }

  // Create the action buttons
  function createActionButtons() {
    // Check if buttons already exist
    if (document.getElementById('jobdiva-goto-bridge-container')) {
      return;
    }

    // Create container
    const container = document.createElement('div');
    container.id = 'jobdiva-goto-bridge-container';
    container.className = 'jobdiva-goto-bridge-buttons';

    // Call button
    const callBtn = document.createElement('button');
    callBtn.id = 'jobdiva-goto-call-btn';
    callBtn.className = 'jobdiva-goto-btn jobdiva-goto-call';
    callBtn.innerHTML = `
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path>
      </svg>
      Call via GoTo
    `;
    callBtn.onclick = handleCallClick;

    // SMS button
    const smsBtn = document.createElement('button');
    smsBtn.id = 'jobdiva-goto-sms-btn';
    smsBtn.className = 'jobdiva-goto-btn jobdiva-goto-sms';
    smsBtn.innerHTML = `
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
      </svg>
      Text via GoTo
    `;
    smsBtn.onclick = handleSmsClick;

    container.appendChild(callBtn);
    container.appendChild(smsBtn);

    // Insert into page (adjust selector based on JobDiva layout)
    const insertionPoint = document.querySelector('.candidate-header') ||
                            document.querySelector('.candidate-details') ||
                            document.body;
    
    if (insertionPoint === document.body) {
      // If we can't find a good insertion point, float it
      container.style.position = 'fixed';
      container.style.top = '100px';
      container.style.right = '20px';
      container.style.zIndex = '10000';
    }

    insertionPoint.insertBefore(container, insertionPoint.firstChild);
  }

  // Handle call button click
  async function handleCallClick() {
    console.log('[JobDiva-GoTo Bridge] Call button clicked');

    const candidate = extractCandidateInfo();
    const recruiter = extractRecruiterInfo();

    if (!candidate || !candidate.candidate_phone) {
      alert('Unable to extract candidate phone number from the page.');
      return;
    }

    if (!confirm(`Initiate call to ${candidate.candidate_name} at ${candidate.candidate_phone}?`)) {
      return;
    }

    try {
      const response = await fetch(`${BACKEND_API_URL}/call/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          candidate_id: candidate.candidate_id,
          candidate_name: candidate.candidate_name,
          candidate_phone: candidate.candidate_phone,
          recruiter_id: recruiter.recruiter_id,
          recruiter_name: recruiter.recruiter_name
        })
      });

      const result = await response.json();

      if (result.success) {
        alert(`Call initiated successfully!\n\nJobDiva note: ${result.jobdiva_note_created ? 'Created' : 'Failed'}`);
      } else {
        alert(`Failed to initiate call: ${result.message}`);
      }
    } catch (error) {
      console.error('[JobDiva-GoTo Bridge] Error initiating call:', error);
      alert(`Error initiating call: ${error.message}`);
    }
  }

  // Handle SMS button click
  async function handleSmsClick() {
    console.log('[JobDiva-GoTo Bridge] SMS button clicked');

    const candidate = extractCandidateInfo();
    const recruiter = extractRecruiterInfo();

    if (!candidate || !candidate.candidate_phone) {
      alert('Unable to extract candidate phone number from the page.');
      return;
    }

    // Show modal for message input
    showSmsModal(candidate, recruiter);
  }

  // Create and show SMS modal
  function showSmsModal(candidate, recruiter) {
    // Remove existing modal if any
    const existingModal = document.getElementById('jobdiva-goto-sms-modal');
    if (existingModal) {
      existingModal.remove();
    }

    // Create modal
    const modal = document.createElement('div');
    modal.id = 'jobdiva-goto-sms-modal';
    modal.className = 'jobdiva-goto-modal';
    modal.innerHTML = `
      <div class="jobdiva-goto-modal-content">
        <div class="jobdiva-goto-modal-header">
          <h3>Send SMS via GoTo</h3>
          <button class="jobdiva-goto-modal-close" id="jobdiva-goto-modal-close">&times;</button>
        </div>
        <div class="jobdiva-goto-modal-body">
          <p><strong>To:</strong> ${candidate.candidate_name} (${candidate.candidate_phone})</p>
          <p><strong>From:</strong> ${recruiter.recruiter_name}</p>
          <textarea 
            id="jobdiva-goto-sms-message" 
            placeholder="Enter your message..." 
            rows="5"
            maxlength="1000"
          ></textarea>
          <div class="jobdiva-goto-char-count">
            <span id="jobdiva-goto-char-count">0</span> / 1000 characters
          </div>
        </div>
        <div class="jobdiva-goto-modal-footer">
          <button class="jobdiva-goto-btn-secondary" id="jobdiva-goto-cancel-btn">Cancel</button>
          <button class="jobdiva-goto-btn-primary" id="jobdiva-goto-send-sms-btn">Send SMS</button>
        </div>
      </div>
    `;

    document.body.appendChild(modal);

    // Event listeners
    const messageTextarea = document.getElementById('jobdiva-goto-sms-message');
    const charCount = document.getElementById('jobdiva-goto-char-count');
    const sendBtn = document.getElementById('jobdiva-goto-send-sms-btn');
    const cancelBtn = document.getElementById('jobdiva-goto-cancel-btn');
    const closeBtn = document.getElementById('jobdiva-goto-modal-close');

    messageTextarea.addEventListener('input', () => {
      charCount.textContent = messageTextarea.value.length;
    });

    sendBtn.addEventListener('click', () => sendSms(candidate, recruiter, messageTextarea.value));
    cancelBtn.addEventListener('click', () => modal.remove());
    closeBtn.addEventListener('click', () => modal.remove());

    // Close on outside click
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        modal.remove();
      }
    });

    // Focus on textarea
    messageTextarea.focus();
  }

  // Send SMS
  async function sendSms(candidate, recruiter, message) {
    if (!message || message.trim().length === 0) {
      alert('Please enter a message.');
      return;
    }

    const modal = document.getElementById('jobdiva-goto-sms-modal');
    const sendBtn = document.getElementById('jobdiva-goto-send-sms-btn');
    
    sendBtn.disabled = true;
    sendBtn.textContent = 'Sending...';

    try {
      const response = await fetch(`${BACKEND_API_URL}/sms/send`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          candidate_id: candidate.candidate_id,
          candidate_name: candidate.candidate_name,
          candidate_phone: candidate.candidate_phone,
          recruiter_id: recruiter.recruiter_id,
          recruiter_name: recruiter.recruiter_name,
          message: message.trim()
        })
      });

      const result = await response.json();

      if (result.success) {
        alert(`SMS sent successfully!\n\nJobDiva note: ${result.jobdiva_note_created ? 'Created' : 'Failed'}`);
        modal.remove();
      } else {
        alert(`Failed to send SMS: ${result.message}`);
        sendBtn.disabled = false;
        sendBtn.textContent = 'Send SMS';
      }
    } catch (error) {
      console.error('[JobDiva-GoTo Bridge] Error sending SMS:', error);
      alert(`Error sending SMS: ${error.message}`);
      sendBtn.disabled = false;
      sendBtn.textContent = 'Send SMS';
    }
  }

  // Initialize
  function init() {
    // Wait for page to fully load
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', init);
      return;
    }

    // Check if we're on a candidate page
    // Adjust this logic based on JobDiva URL structure
    const isCandidate Page = window.location.href.includes('candidate') || 
                             window.location.href.includes('Candidate');

    if (isCandidatePage) {
      console.log('[JobDiva-GoTo Bridge] Candidate page detected, initializing...');
      currentCandidate = extractCandidateInfo();
      currentRecruiter = extractRecruiterInfo();
      createActionButtons();
    }
  }

  // Run initialization
  init();

  // Listen for page changes (for SPAs)
  let lastUrl = location.href;
  new MutationObserver(() => {
    const url = location.href;
    if (url !== lastUrl) {
      lastUrl = url;
      init();
    }
  }).observe(document, { subtree: true, childList: true });

})();
