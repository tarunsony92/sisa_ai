// Configuration
const API_BASE_URL = 'http://localhost:8000';
let currentResults = null;

// DOM Elements
const analyzeBtn = document.getElementById('analyzeBtn');
const uploadBtn = document.getElementById('uploadBtn');
const textInput = document.getElementById('textInput');
const inputType = document.getElementById('inputType');
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const tabButtons = document.querySelectorAll('.tab-button');
const tabContents = document.querySelectorAll('.tab-content');

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    setupTabs();
    setupFileUpload();
    setupAnalysis();
    checkAPIStatus();
});

// Tab Navigation
function setupTabs() {
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
}

function switchTab(tabName) {
    // Update tab buttons
    tabButtons.forEach(btn => btn.classList.remove('active'));
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    // Update tab contents
    tabContents.forEach(content => content.classList.remove('active'));
    document.getElementById(tabName).classList.add('active');
}

// File Upload Setup
function setupFileUpload() {
    // Click to upload
    uploadArea.addEventListener('click', () => fileInput.click());

    // File input change
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            displayFileInfo(file);
        }
    });

    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        const file = e.dataTransfer.files[0];
        if (file) {
            fileInput.files = e.dataTransfer.files;
            displayFileInfo(file);
        }
    });

    // Upload button
    uploadBtn.addEventListener('click', () => analyzeFile());
}

function displayFileInfo(file) {
    document.getElementById('fileName').textContent = file.name;
    document.getElementById('fileSize').textContent = formatFileSize(file.size);
    document.getElementById('fileInfo').classList.remove('hidden');
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Analysis Setup
function setupAnalysis() {
    analyzeBtn.addEventListener('click', analyzeText);
}

async function analyzeText() {
    const content = textInput.value.trim();
    if (!content) {
        alert('Please enter some content to analyze');
        return;
    }

    const type = inputType.value;
    
    try {
        showLoading(true);
        
        const request = {
            input_type: type,
            content: content,
            options: getOptions()
        };

        const response = await fetch(`${API_BASE_URL}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(request)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Analysis failed');
        }

        const results = await response.json();
        displayResults(results);
        switchTab('results');
        showLoading(false);

    } catch (error) {
        showLoading(false);
        showError(`Analysis failed: ${error.message}`);
    }
}

async function analyzeFile() {
    const file = fileInput.files[0];
    if (!file) {
        alert('Please select a file');
        return;
    }

    try {
        showLoading(true);

        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_BASE_URL}/analyze/file`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'File analysis failed');
        }

        const results = await response.json();
        displayResults(results);
        switchTab('results');
        showLoading(false);

    } catch (error) {
        showLoading(false);
        showError(`File analysis failed: ${error.message}`);
    }
}

function getOptions() {
    return {
        mask: document.getElementById('maskOption').checked,
        block_high_risk: document.getElementById('blockHighRiskOption').checked,
        log_analysis: document.getElementById('logAnalysisOption').checked,
        ai_insights: document.getElementById('aiInsightsOption').checked
    };
}

// Results Display
function displayResults(results) {
    currentResults = results;

    // Hide no results message
    document.getElementById('noResults').style.display = 'none';
    document.getElementById('resultsContainer').style.display = 'block';

    // Update summary
    document.getElementById('summaryText').textContent = results.summary;
    document.getElementById('riskScore').textContent = results.risk_score;
    document.getElementById('findingsCount').textContent = results.findings.length;

    // Update risk level badge
    const badge = document.getElementById('riskLevelBadge');
    badge.className = `risk-badge ${results.risk_level}`;
    badge.textContent = results.risk_level.toUpperCase();

    // Update risk breakdown
    updateRiskBreakdown(results.findings);

    // Display findings
    displayFindings(results.findings);

    // Display insights if available
    if (results.insights && results.insights.length > 0) {
        displayInsights(results.insights);
    }

    // Display masked content if available
    if (results.masked_content) {
        document.getElementById('maskedContentCard').style.display = 'block';
        document.getElementById('maskedContent').textContent = results.masked_content;
    }

    // Display recommendations
    displayRecommendations(results.findings);

    // Scroll to results
    document.getElementById('resultsContainer').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function updateRiskBreakdown(findings) {
    const breakdown = {
        critical: 0,
        high: 0,
        medium: 0,
        low: 0
    };

    findings.forEach(finding => {
        breakdown[finding.risk]++;
    });

    document.getElementById('criticalCount').textContent = breakdown.critical;
    document.getElementById('highCount').textContent = breakdown.high;
    document.getElementById('mediumCount').textContent = breakdown.medium;
    document.getElementById('lowCount').textContent = breakdown.low;
}

function displayFindings(findings) {
    if (!findings || findings.length === 0) {
        document.getElementById('findingsTable').innerHTML = '<p style="color: #10b981;">✓ No security issues detected!</p>';
        return;
    }

    let html = '<table><thead><tr>' +
        '<th>Type</th>' +
        '<th>Risk Level</th>' +
        '<th>Line</th>' +
        '<th>Details</th>' +
        '</tr></thead><tbody>';

    findings.forEach(finding => {
        const riskClass = finding.risk.toLowerCase();
        const context = finding.context ? finding.context.substring(0, 50) + '...' : 'N/A';
        
        html += `<tr>
            <td><strong>${finding.type}</strong></td>
            <td><span class="risk-badge ${riskClass}">${finding.risk}</span></td>
            <td>${finding.line || 'N/A'}</td>
            <td title="${finding.context || ''}" style="color: #666; font-size: 12px;">${context}</td>
        </tr>`;
    });

    html += '</tbody></table>';
    document.getElementById('findingsTable').innerHTML = html;
}

function displayInsights(insights) {
    document.getElementById('insightsCard').style.display = 'block';
    
    let html = '';
    insights.forEach(insight => {
        html += `<div class="insight-item">
            <span class="insight-icon">💡</span>
            <span class="insight-text">${escapeHtml(insight)}</span>
        </div>`;
    });

    document.getElementById('insightsList').innerHTML = html;
}

function displayRecommendations(findings) {
    document.getElementById('recommendationsCard').style.display = 'block';

    const recommendations = new Set();

    // Generic recommendations based on findings
    const hasPassword = findings.some(f => f.type === 'password');
    const hasApiKey = findings.some(f => f.type === 'api_key');
    const hasToken = findings.some(f => f.type === 'token');
    const hasEmail = findings.some(f => f.type === 'email');
    const hasStackTrace = findings.some(f => f.type === 'stack_trace');
    const hasSqlInjection = findings.some(f => f.type === 'sql_injection');
    const criticalCount = findings.filter(f => f.risk === 'critical').length;

    if (hasPassword) {
        recommendations.add('🔐 Rotate all exposed passwords immediately');
        recommendations.add('⚠️ Review password storage policies and implement strong encryption');
    }

    if (hasApiKey) {
        recommendations.add('🔑 Revoke and regenerate exposed API keys');
        recommendations.add('📋 Implement API key rotation policy');
    }

    if (hasToken) {
        recommendations.add('🎫 Invalidate and reissue authentication tokens');
        recommendations.add('🔄 Implement token expiration and refresh mechanisms');
    }

    if (hasEmail) {
        recommendations.add('📧 Review data exposure in logs');
        recommendations.add('🛡️ Implement email masking in logging systems');
    }

    if (hasStackTrace) {
        recommendations.add('📚 Configure logging to exclude stack traces in production');
        recommendations.add('🔍 Enable error tracking with secure context');
    }

    if (hasSqlInjection) {
        recommendations.add('💾 Use parameterized queries and prepared statements');
        recommendations.add('✓ Implement input validation and sanitization');
    }

    if (criticalCount > 0) {
        recommendations.add('🚨 Conduct immediate security review');
        recommendations.add('📞 Notify security team and stakeholders');
    }

    if (findings.length > 10) {
        recommendations.add('🏢 Implement comprehensive secret management system');
        recommendations.add('📊 Enable centralized log analysis and monitoring');
    }

    let html = '';
    Array.from(recommendations).forEach(rec => {
        html += `<div class="recommendation-item">
            <span class="recommendation-icon"></span>
            <span class="recommendation-text">${escapeHtml(rec)}</span>
        </div>`;
    });

    if (html) {
        document.getElementById('recommendationsList').innerHTML = html;
    }
}

// Utility Functions
function showLoading(show) {
    if (show) {
        analyzeBtn.disabled = true;
        uploadBtn.disabled = true;
        analyzeBtn.innerHTML = '<span class="loading"></span> Analyzing...';
        uploadBtn.innerHTML = '<span class="loading"></span> Uploading...';
    } else {
        analyzeBtn.disabled = false;
        uploadBtn.disabled = false;
        analyzeBtn.innerHTML = '<span class="btn-icon">🔍</span> Analyze';
        uploadBtn.innerHTML = '<span class="btn-icon">⬆️</span> Upload & Analyze';
    }
}

function showError(message) {
    alert('Error: ' + message);
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

function copyToClipboard() {
    const content = document.getElementById('maskedContent').textContent;
    navigator.clipboard.writeText(content).then(() => {
        alert('Masked content copied to clipboard!');
    }).catch(err => {
        console.error('Failed to copy:', err);
    });
}

async function checkAPIStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            updateStatus(true);
        } else {
            updateStatus(false);
        }
    } catch {
        updateStatus(false);
    }
}

function updateStatus(online) {
    const statusDot = document.getElementById('apiStatus');
    const statusText = document.getElementById('statusText');
    
    if (online) {
        statusDot.classList.remove('offline');
        statusDot.classList.add('online');
        statusText.textContent = 'Online';
    } else {
        statusDot.classList.remove('online');
        statusDot.classList.add('offline');
        statusText.textContent = 'Offline';
    }
}

// Check API status periodically
setInterval(checkAPIStatus, 30000);
