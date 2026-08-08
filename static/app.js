// State management
let candidatesList = [];
let curriculumData = null;
let selectedCandidate = null;
let activeSessionId = null;
let currentStep = 0;
let isWaitingForServer = false;

// HTML escaping helper to prevent XSS vulnerabilities
function escapeHTML(str) {
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// Escape HTML and format line breaks safely
function formatMessageText(str) {
  return escapeHTML(str).replace(/\n/g, '<br>');
}

// DOM Elements
const candidatesContainer = document.getElementById('candidates-container');
const candidateSearchInput = document.getElementById('candidate-search');
const timelineContainer = document.getElementById('timeline-container');
const chatMessagesContainer = document.getElementById('chat-messages-container');
const chatInput = document.getElementById('chat-input');
const chatSendBtn = document.getElementById('chat-send-btn');
const startInterviewBtn = document.getElementById('start-interview-btn');
const finishInterviewBtn = document.getElementById('finish-interview-btn');
const providerBadge = document.getElementById('provider-badge');
const providerLabel = document.getElementById('provider-label');
const openSettingsBtn = document.getElementById('open-settings-btn');
const closeSettingsBtn = document.getElementById('close-settings-btn');
const cancelSettingsBtn = document.getElementById('cancel-settings-btn');
const saveSettingsBtn = document.getElementById('save-settings-btn');
const settingsModal = document.getElementById('settings-modal');
const typingIndicator = document.getElementById('typing-indicator');
const progressBar = document.getElementById('progress-bar');
const progressText = document.getElementById('progress-text');

// API endpoint URL base (relative because we host them together)
const API_BASE = "";

// Initialize App
async function init() {
  setupEventListeners();
  await fetchCurriculum();
  await fetchCandidates();
  await checkServerSettings();
}

// Event Listeners
function setupEventListeners() {
  // Candidate search filtering
  candidateSearchInput.addEventListener('input', filterCandidates);
  
  // Settings modal controls
  openSettingsBtn.addEventListener('click', openSettings);
  closeSettingsBtn.addEventListener('click', closeSettings);
  cancelSettingsBtn.addEventListener('click', closeSettings);
  saveSettingsBtn.addEventListener('click', saveSettings);
  
  // Chat send controls
  chatSendBtn.addEventListener('click', sendUserMessage);
  chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      sendUserMessage();
    }
  });
  
  // Interview actions
  startInterviewBtn.addEventListener('click', startInterviewSession);
  finishInterviewBtn.addEventListener('click', () => {
    switchScreen('empty-screen');
    selectedCandidate = null;
    document.querySelectorAll('.candidate-card').forEach(c => c.classList.remove('active'));
  });
}

// Fetch curriculum
async function fetchCurriculum() {
  try {
    const response = await fetch(`${API_BASE}/api/curriculum`);
    if (!response.ok) throw new Error('Failed to load curriculum');
    curriculumData = await response.json();
  } catch (error) {
    console.error('Curriculum error:', error);
  }
}

// Fetch Candidates list
async function fetchCandidates() {
  try {
    const response = await fetch(`${API_BASE}/api/candidates`);
    if (!response.ok) throw new Error('Failed to load candidates');
    const data = await response.json();
    candidatesList = data.candidates || [];
    renderCandidatesList(candidatesList);
  } catch (error) {
    candidatesContainer.innerHTML = `
      <div class="loading-state" style="color: var(--rose);">
        <p>Error loading candidates: ${error.message}</p>
      </div>
    `;
  }
}

// Check Server active LLM settings
async function checkServerSettings() {
  try {
    const response = await fetch(`${API_BASE}/api/settings`);
    if (!response.ok) throw new Error('Failed to fetch settings');
    const settings = await response.json();
    updateProviderIndicator(settings.active_provider);
    
    // Fill in placeholders if configured
    if (settings.openrouter_configured) {
      document.getElementById('openrouter-key').placeholder = '••••••••••••••••••••';
    }
    if (settings.gemini_configured) {
      document.getElementById('gemini-key').placeholder = '••••••••••••••••••••';
    }
    if (settings.openai_configured) {
      document.getElementById('openai-key').placeholder = '••••••••••••••••••••';
    }
  } catch (error) {
    console.error('Settings fetch error:', error);
  }
}

// Update settings on server
async function saveSettings() {
  const openrouterKey = document.getElementById('openrouter-key').value;
  const geminiKey = document.getElementById('gemini-key').value;
  const openaiKey = document.getElementById('openai-key').value;
  
  saveSettingsBtn.disabled = true;
  saveSettingsBtn.innerText = 'Configuring...';
  
  try {
    const response = await fetch(`${API_BASE}/api/settings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        openrouter_key: openrouterKey === "" ? "" : (openrouterKey || null),
        gemini_key: geminiKey === "" ? "" : (geminiKey || null),
        openai_key: openaiKey === "" ? "" : (openaiKey || null)
      })
    });
    
    if (!response.ok) throw new Error('Failed to save settings');
    const data = await response.json();
    updateProviderIndicator(data.active_provider);
    closeSettings();
  } catch (error) {
    alert(`Configuration Error: ${error.message}`);
  } finally {
    saveSettingsBtn.disabled = false;
    saveSettingsBtn.innerText = 'Save Configuration';
  }
}

// Update Provider Badges
function updateProviderIndicator(provider) {
  providerBadge.className = 'status-indicator';
  if (provider === 'openrouter') {
    providerBadge.className = 'status-indicator active-provider';
    providerLabel.innerText = 'OpenRouter Active';
  } else if (provider === 'gemini') {
    providerBadge.className = 'status-indicator active-provider';
    providerLabel.innerText = 'Gemini AI Active';
  } else if (provider === 'openai') {
    providerBadge.className = 'status-indicator active-provider';
    providerLabel.innerText = 'OpenAI Active';
  } else {
    providerBadge.className = 'status-indicator mock';
    providerLabel.innerText = 'No Provider Configured (API Key Required)';
  }
}

// Render candidates list
function renderCandidatesList(list) {
  candidatesContainer.innerHTML = '';
  
  if (list.length === 0) {
    candidatesContainer.innerHTML = `
      <div class="loading-state">
        <p>No candidates found matching the search.</p>
      </div>
    `;
    return;
  }
  
  list.forEach(candidate => {
    const card = document.createElement('div');
    card.className = 'candidate-card';
    card.dataset.id = candidate.member.id;
    
    const isCompleted = candidate.member.status === 'COMPLETED';
    const badgeClass = isCompleted ? 'completed' : 'in-progress';
    const badgeLabel = isCompleted ? 'Completed' : 'In Progress';
    
    card.innerHTML = `
      <div class="card-top">
        <span class="candidate-name">${escapeHTML(candidate.member.name)}</span>
        <span class="cand-id">${escapeHTML(candidate.member.id)}</span>
      </div>
      <span class="candidate-role">${escapeHTML(candidate.member.jobRole)}</span>
      <div class="card-meta">
        <span class="candidate-exp">${escapeHTML(candidate.member.yearsExperience)} yrs exp</span>
        <span class="completion-badge ${badgeClass}">${escapeHTML(badgeLabel)}</span>
      </div>
    `;
    
    card.addEventListener('click', () => selectCandidate(candidate.member.id, card));
    candidatesContainer.appendChild(card);
  });
}

// Filter candidates on search input
function filterCandidates() {
  const query = candidateSearchInput.value.toLowerCase();
  const filtered = candidatesList.filter(c => {
    return c.member.name.toLowerCase().includes(query) ||
           c.member.jobRole.toLowerCase().includes(query) ||
           c.member.id.toLowerCase().includes(query);
  });
  renderCandidatesList(filtered);
}

// Switch between screens
function switchScreen(screenId) {
  document.querySelectorAll('.screen').forEach(screen => {
    screen.classList.remove('active');
  });
  document.getElementById(screenId).classList.add('active');
}

// Select candidate
function selectCandidate(candidateId, cardElement) {
  // Highlight selected card
  document.querySelectorAll('.candidate-card').forEach(c => c.classList.remove('active'));
  if (cardElement) cardElement.classList.add('active');
  
  // Find candidate details
  selectedCandidate = candidatesList.find(c => c.member.id === candidateId);
  if (!selectedCandidate) return;
  
  // Update Profile screen fields
  document.getElementById('profile-name').innerText = selectedCandidate.member.name;
  document.getElementById('profile-role').innerText = selectedCandidate.member.jobRole;
  document.getElementById('profile-avatar').innerText = selectedCandidate.member.name.charAt(0);
  document.getElementById('profile-edu').innerText = selectedCandidate.member.education;
  document.getElementById('profile-exp').innerText = `${selectedCandidate.member.yearsExperience} Year${selectedCandidate.member.yearsExperience === 1 ? '' : 's'}`;
  
  const statusElement = document.getElementById('profile-status');
  statusElement.className = 'info-val';
  if (selectedCandidate.member.status === 'COMPLETED') {
    statusElement.classList.add('badge-completed');
    statusElement.innerText = 'Completed';
  } else {
    statusElement.innerText = 'In Progress';
  }
  
  // Update signals
  document.getElementById('stat-commits').innerText = selectedCandidate.signals.commitDays;
  document.getElementById('stat-completed').innerText = selectedCandidate.signals.missionsCompleted;
  document.getElementById('stat-firsttry').innerText = selectedCandidate.signals.missionsFirstTry;
  
  // Render timeline grid
  renderTimeline(selectedCandidate.missions);
  
  // Open the profile screen
  switchScreen('profile-screen');
}

// Render missions timeline
function renderTimeline(candidateMissions) {
  timelineContainer.innerHTML = '';
  
  // We want to render a box for each day (1 to 31)
  for (let day = 1; day <= 31; day++) {
    const dayBox = document.createElement('div');
    dayBox.className = 'day-box';
    
    // Find if the candidate did this mission
    const mission = candidateMissions.find(m => m.day === day);
    
    let statusClass = 'skipped';
    let attemptsLabel = 'Skipped';
    let titleText = `Day ${day}: No record`;
    
    if (mission) {
      titleText = `Day ${day}: ${mission.title}`;
      if (mission.skipped) {
        statusClass = 'skipped';
        attemptsLabel = 'Skipped';
      } else if (mission.passed) {
        statusClass = 'passed';
        attemptsLabel = `${mission.attempts || 1} Attempt${mission.attempts === 1 ? '' : 's'}`;
      } else {
        statusClass = 'attempted';
        attemptsLabel = `${mission.attempts || 0} Attempt${mission.attempts === 1 ? '' : 's'}`;
      }
    } else {
      // Find title from curriculum data if available
      if (curriculumData) {
        const cDay = curriculumData.days.find(d => d.day === day);
        if (cDay) titleText = `Day ${day}: ${cDay.title}`;
      }
    }
    
    dayBox.classList.add(statusClass);
    dayBox.title = titleText;
    dayBox.innerHTML = `
      <span class="day-number">Day ${day}</span>
      <span class="day-label">${mission ? truncateText(mission.title, 14) : 'Setup/Build'}</span>
      <span class="day-attempts">${attemptsLabel}</span>
    `;
    
    timelineContainer.appendChild(dayBox);
  }
}

// Start Interview Session
async function startInterviewSession() {
  if (!selectedCandidate) return;
  
  activeSessionId = `sess-${Math.random().toString(36).substr(2, 9)}`;
  currentStep = 0;
  chatMessagesContainer.innerHTML = '';
  
  // Configure chat header
  document.getElementById('chat-candidate-name').innerText = selectedCandidate.member.name;
  document.getElementById('chat-candidate-role').innerText = selectedCandidate.member.jobRole;
  
  updateProgressBar(0, "Warming up session...");
  switchScreen('chat-screen');
  
  isWaitingForServer = true;
  setTypingIndicator(true, "Interviewer is preparing session details...");
  
  try {
    const response = await fetch(`${API_BASE}/api/interview`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        sessionId: activeSessionId,
        candidate: selectedCandidate
      })
    });
    
    if (!response.ok) throw new Error('Failed to start interview server turn');
    const data = await response.json();
    
    appendMessage('interviewer', data.reply);
    currentStep = 1;
    updateProgressBar(1, "Topic 1: Intro & Warmup");
  } catch (error) {
    appendMessage('interviewer', `Error starting interview: ${error.message}. Please try again.`);
  } finally {
    isWaitingForServer = false;
    setTypingIndicator(false);
  }
}

// Send user chat message
async function sendUserMessage() {
  const text = chatInput.value.trim();
  if (!text || isWaitingForServer) return;
  
  chatInput.value = '';
  appendMessage('candidate', text);
  
  isWaitingForServer = true;
  setTypingIndicator(true, "Interviewer is analyzing response and drafting follow-up...");
  
  try {
    const response = await fetch(`${API_BASE}/api/interview`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        sessionId: activeSessionId,
        message: text
      })
    });
    
    if (!response.ok) throw new Error('API Request failed');
    const data = await response.json();
    
    if (data.done) {
      appendMessage('interviewer', data.reply);
      setTypingIndicator(true, "Compiling final feedback assessment report...");
      setTimeout(() => {
        setTypingIndicator(false);
        renderFeedbackReport(data.feedback);
      }, 2000);
    } else {
      appendMessage('interviewer', data.reply);
      currentStep++;
      
      // Update progress bar based on steps
      let topic = "Topic Assessment";
      if (currentStep <= 2) topic = "Topic 1: Warmup & General AI Core";
      else if (currentStep <= 4) topic = "Topic 2: Retrieval & Engine Details";
      else if (currentStep <= 6) topic = "Topic 3: Prompting & Fine-Tuning";
      else topic = "Topic 4: Agents, MCP & Deployment";
      
      updateProgressBar(currentStep, topic);
    }
  } catch (error) {
    appendMessage('interviewer', `Communication error: ${error.message}. Please resend.`);
  } finally {
    isWaitingForServer = false;
    if (currentStep < 9) setTypingIndicator(false);
  }
}

// Append Chat Bubbles
function appendMessage(sender, text) {
  const wrapper = document.createElement('div');
  wrapper.className = `message-wrapper ${sender}`;
  
  const initial = sender === 'interviewer' ? 'AI' : selectedCandidate.member.name.charAt(0);
  const displayName = sender === 'interviewer' ? 'Interviewer Agent' : selectedCandidate.member.name;
  
  wrapper.innerHTML = `
    <div class="msg-avatar">${escapeHTML(initial)}</div>
    <div class="msg-body">
      <span class="msg-sender">${escapeHTML(displayName)}</span>
      <div class="msg-bubble">${formatMessageText(text)}</div>
    </div>
  `;
  
  chatMessagesContainer.appendChild(wrapper);
  chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
}

// Update progress bar UI
function updateProgressBar(step, topicName) {
  // Max steps is 8 conversation turns + feedback
  const pct = Math.min(100, Math.round((step / 9) * 100));
  progressBar.style.width = `${pct}%`;
  progressText.innerText = `${topicName} (${pct}%)`;
}

// Set typing indicator state
function setTypingIndicator(visible, text = "Interviewer is writing...") {
  typingIndicator.querySelector('.typing-text').innerText = text;
  typingIndicator.style.display = visible ? 'flex' : 'none';
  chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
}

// Render Feedback Report screen
function renderFeedbackReport(feedback) {
  if (!feedback) return;
  
  document.getElementById('report-name').innerText = selectedCandidate.member.name;
  document.getElementById('report-role').innerText = selectedCandidate.member.jobRole;
  document.getElementById('report-avatar').innerText = selectedCandidate.member.name.charAt(0);
  document.getElementById('report-summary-text').innerText = feedback.summary;
  
  // Set HIRE / NO HIRE decision badge
  const decisionBadge = document.getElementById('report-decision-badge');
  if (decisionBadge) {
    const isHire = feedback.decision && feedback.decision.toUpperCase().includes('HIRE') && !feedback.decision.toUpperCase().includes('NO');
    if (isHire) {
      decisionBadge.innerText = 'HIRE';
      decisionBadge.className = 'decision-badge hire';
    } else {
      decisionBadge.innerText = 'NO HIRE';
      decisionBadge.className = 'decision-badge no-hire';
    }
  }
  
  // Strengths list
  const strengthsList = document.getElementById('report-strengths-list');
  strengthsList.innerHTML = '';
  feedback.strengths.forEach(s => {
    const li = document.createElement('li');
    li.innerText = s;
    strengthsList.appendChild(li);
  });
  
  // Gaps list
  const gapsList = document.getElementById('report-gaps-list');
  gapsList.innerHTML = '';
  feedback.gaps.forEach(g => {
    const li = document.createElement('li');
    li.innerText = g;
    gapsList.appendChild(li);
  });
  
  // Next steps list
  const nextContainer = document.getElementById('report-next-container');
  nextContainer.innerHTML = '';
  feedback.next.forEach((step, index) => {
    const actionCard = document.createElement('div');
    actionCard.className = 'action-card';
    actionCard.innerHTML = `
      <div class="action-num">${index + 1}</div>
      <div class="action-text">${escapeHTML(step)}</div>
    `;
    nextContainer.appendChild(actionCard);
  });
  
  switchScreen('feedback-screen');
}

// Settings modal trigger
function openSettings() {
  settingsModal.style.display = 'flex';
}

function closeSettings() {
  settingsModal.style.display = 'none';
  // Clear keys on close
  document.getElementById('openrouter-key').value = '';
  document.getElementById('gemini-key').value = '';
  document.getElementById('openai-key').value = '';
}

// Helper: Truncate strings
function truncateText(str, maxLen) {
  if (str.length > maxLen) {
    return str.substring(0, maxLen - 3) + '...';
  }
  return str;
}

// Start app
window.addEventListener('DOMContentLoaded', init);
