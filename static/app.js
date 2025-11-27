// Bose Professional Technical Assistant - Frontend Logic

const API_BASE = window.location.origin;
let isProcessing = false;

// DOM Elements
const messagesArea = document.getElementById('messagesArea');
const queryForm = document.getElementById('queryForm');
const queryInput = document.getElementById('queryInput');
const submitBtn = document.getElementById('submitBtn');
const statusDot = document.getElementById('statusDot');
const statusText = document.getElementById('statusText');
const modelInfo = document.getElementById('modelInfo');
const docCount = document.getElementById('docCount');
const systemStatus = document.getElementById('systemStatus');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkHealth();
    loadSystemInfo();
    setupEventListeners();
    
    // Auto-resize textarea
    queryInput.addEventListener('input', autoResize);
    
    // Check health every 30 seconds
    setInterval(checkHealth, 30000);
});

function setupEventListeners() {
    queryForm.addEventListener('submit', handleSubmit);
    
    // Handle Enter key (submit) and Shift+Enter (new line)
    queryInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
        }
    });
}

function autoResize() {
    queryInput.style.height = 'auto';
    queryInput.style.height = queryInput.scrollHeight + 'px';
}

async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE}/api/health`);
        const data = await response.json();
        
        if (data.status === 'healthy') {
            statusDot.classList.add('connected');
            statusText.textContent = 'Online';
            docCount.textContent = data.document_count;
        } else {
            statusDot.classList.remove('connected');
            statusText.textContent = 'Initializing...';
        }
    } catch (error) {
        statusDot.classList.remove('connected');
        statusText.textContent = 'Offline';
        console.error('Health check failed:', error);
    }
}

async function loadSystemInfo() {
    try {
        const response = await fetch(`${API_BASE}/api/info`);
        const data = await response.json();
        
        modelInfo.textContent = data.model.name || 'Phi-2';
        docCount.textContent = data.document_count;
        systemStatus.textContent = data.documents_loaded ? 'Ready' : 'No Documents';
        
        if (!data.documents_loaded) {
            showWarning('No documents loaded. Please process documents first.');
        }
    } catch (error) {
        console.error('Failed to load system info:', error);
        modelInfo.textContent = 'Unknown';
        systemStatus.textContent = 'Error';
    }
}

async function handleSubmit(e) {
    e.preventDefault();
    
    const question = queryInput.value.trim();
    if (!question || isProcessing) return;
    
    // Clear input and reset height
    queryInput.value = '';
    queryInput.style.height = 'auto';
    
    // Add user message
    addMessage('user', question);
    
    // Show loading indicator
    const loadingId = addLoadingMessage();
    
    // Disable input
    isProcessing = true;
    submitBtn.disabled = true;
    queryInput.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE}/api/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question, verbose: false })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Query failed');
        }
        
        const data = await response.json();
        
        // Remove loading indicator
        removeLoadingMessage(loadingId);
        
        // Add assistant response
        if (data.status === 'success') {
            addMessage('assistant', data.answer, data.sources, data.time);
        } else if (data.status === 'no_context') {
            addMessage('assistant', data.answer, [], data.time);
        } else {
            throw new Error(data.error || 'Unknown error');
        }
        
    } catch (error) {
        removeLoadingMessage(loadingId);
        addErrorMessage(error.message);
        console.error('Query failed:', error);
    } finally {
        // Re-enable input
        isProcessing = false;
        submitBtn.disabled = false;
        queryInput.disabled = false;
        queryInput.focus();
    }
}

function addMessage(type, content, sources = [], time = '') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${type}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    if (type === 'user') {
        contentDiv.textContent = content;
    } else {
        // Assistant message with formatted content
        contentDiv.innerHTML = formatContent(content);
        
        // Add sources if available
        if (sources && sources.length > 0) {
            const sourcesDiv = document.createElement('div');
            sourcesDiv.className = 'message-sources';
            sourcesDiv.innerHTML = `
                <h4>Sources (${sources.length} documents)</h4>
                ${sources.map(src => `
                    <div class="source-item">
                        <span class="source-page">Page ${src.page}</span>
                        <span class="source-type">${src.content_type}</span>
                    </div>
                `).join('')}
            `;
            contentDiv.appendChild(sourcesDiv);
        }
    }
    
    messageDiv.appendChild(contentDiv);
    
    // Add timestamp
    if (time) {
        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = `Answered in ${time}`;
        messageDiv.appendChild(timeDiv);
    }
    
    // Remove welcome message if present
    const welcomeMsg = messagesArea.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }
    
    messagesArea.appendChild(messageDiv);
    messagesArea.scrollTop = messagesArea.scrollHeight;
}

function formatContent(content) {
    // Convert markdown-style formatting to HTML
    let formatted = content
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/\n/g, '<br>');
    
    return formatted;
}

function addLoadingMessage() {
    const loadingId = 'loading-' + Date.now();
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message message-assistant';
    messageDiv.id = loadingId;
    
    messageDiv.innerHTML = `
        <div class="loading-indicator">
            <div class="loading-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    
    messagesArea.appendChild(messageDiv);
    messagesArea.scrollTop = messagesArea.scrollHeight;
    
    return loadingId;
}

function removeLoadingMessage(loadingId) {
    const loadingMsg = document.getElementById(loadingId);
    if (loadingMsg) {
        loadingMsg.remove();
    }
}

function addErrorMessage(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = `Error: ${message}`;
    
    messagesArea.appendChild(errorDiv);
    messagesArea.scrollTop = messagesArea.scrollHeight;
    
    // Auto-remove after 5 seconds
    setTimeout(() => errorDiv.remove(), 5000);
}

function showWarning(message) {
    const warningDiv = document.createElement('div');
    warningDiv.className = 'error-message';
    warningDiv.style.background = 'rgba(255, 165, 0, 0.1)';
    warningDiv.style.borderColor = '#ffa000';
    warningDiv.style.color = '#ffb74d';
    warningDiv.textContent = message;
    
    const infoCard = document.getElementById('infoCard');
    infoCard.parentNode.insertBefore(warningDiv, infoCard.nextSibling);
}
