// LUCIFEROS Web Dashboard JavaScript

class LuciferOSDashboard {
    constructor() {
        this.eventSource = null;
        this.systemStatus = {};
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.startSystemMonitoring();
        this.loadInitialData();
    }

    setupEventListeners() {
        // Attack controls
        document.getElementById('start-attack-btn')?.addEventListener('click', () => this.startAttack());
        document.getElementById('stop-attack-btn')?.addEventListener('click', () => this.stopAttack());

        // AI query
        document.getElementById('send-ai-query-btn')?.addEventListener('click', () => this.sendAIQuery());

        // Browser controls
        document.getElementById('browser-navigate-btn')?.addEventListener('click', () => this.browserNavigate());
        document.getElementById('browser-screenshot-btn')?.addEventListener('click', () => this.browserScreenshot());

        // Recon controls
        document.getElementById('start-recon-btn')?.addEventListener('click', () => this.startRecon());

        // Payload controls
        document.getElementById('generate-payload-btn')?.addEventListener('click', () => this.generatePayload());

        // OpenClaw integration
        document.getElementById('open-openclaw-btn')?.addEventListener('click', () => this.openOpenClaw());

        // Emergency stop
        document.getElementById('emergency-stop-btn')?.addEventListener('click', () => this.emergencyStop());
    }

    async loadInitialData() {
        try {
            await this.updateSystemStatus();
            await this.loadLogs();
        } catch (error) {
            console.error('Failed to load initial data:', error);
            this.showAlert('Failed to load initial data', 'danger');
        }
    }

    startSystemMonitoring() {
        // Update system status every 5 seconds
        setInterval(() => this.updateSystemStatus(), 5000);

        // Start log streaming
        this.startLogStreaming();
    }

    async updateSystemStatus() {
        try {
            const response = await fetch('/api/system/status');
            const status = await response.json();

            this.systemStatus = status;
            this.updateStatusDisplay(status);
        } catch (error) {
            console.error('Failed to update system status:', error);
        }
    }

    updateStatusDisplay(status) {
        const statusElement = document.getElementById('system-status');
        if (!statusElement) return;

        let statusClass = 'bg-secondary';
        let statusIcon = 'fa-circle text-warning';
        let statusText = 'Unknown';

        if (status.backend && status.gateway) {
            statusClass = 'bg-success';
            statusIcon = 'fa-circle text-success';
            statusText = 'All Systems Operational';
        } else if (status.backend || status.gateway) {
            statusClass = 'bg-warning';
            statusIcon = 'fa-circle text-warning';
            statusText = 'Partial Systems Online';
        } else {
            statusClass = 'bg-danger';
            statusIcon = 'fa-circle text-danger';
            statusText = 'Systems Offline';
        }

        statusElement.className = `badge ${statusClass} me-2`;
        statusElement.innerHTML = `<i class="fas ${statusIcon}"></i> ${statusText}`;
    }

    async loadLogs() {
        try {
            const response = await fetch('/api/logs');
            const data = await response.json();

            const logContainer = document.getElementById('log-container');
            if (logContainer && data.logs) {
                logContainer.innerHTML = data.logs.map(log =>
                    `<div class="log-entry">${this.escapeHtml(log)}</div>`
                ).join('');
                logContainer.scrollTop = logContainer.scrollHeight;
            }
        } catch (error) {
            console.error('Failed to load logs:', error);
        }
    }

    startLogStreaming() {
        if (this.eventSource) {
            this.eventSource.close();
        }

        this.eventSource = new EventSource('/api/logs/stream');

        this.eventSource.onmessage = (event) => {
            const newLogs = JSON.parse(event.data);
            this.appendLogs(newLogs);
        };

        this.eventSource.onerror = (error) => {
            console.error('Log streaming error:', error);
            // Attempt to reconnect after 5 seconds
            setTimeout(() => this.startLogStreaming(), 5000);
        };
    }

    appendLogs(logs) {
        const logContainer = document.getElementById('log-container');
        if (!logContainer) return;

        logs.forEach(log => {
            const logEntry = document.createElement('div');
            logEntry.className = 'log-entry';
            logEntry.textContent = log;
            logContainer.appendChild(logEntry);
        });

        logContainer.scrollTop = logContainer.scrollHeight;

        // Keep only last 1000 entries
        while (logContainer.children.length > 1000) {
            logContainer.removeChild(logContainer.firstChild);
        }
    }

    async startAttack() {
        const target = document.getElementById('target-input')?.value || '';
        const mode = document.getElementById('attack-mode')?.value || 'recon';

        if (!target) {
            this.showAlert('Please enter a target', 'warning');
            return;
        }

        try {
            const response = await fetch('/api/attack/start/' + mode, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ target: target })
            });

            const result = await response.json();

            if (response.ok) {
                this.showAlert(`Attack started: ${mode} on ${target}`, 'success');
                this.updateProgressDisplay(mode, target);
            } else {
                this.showAlert(result.error || 'Failed to start attack', 'danger');
            }
        } catch (error) {
            console.error('Attack start error:', error);
            this.showAlert('Failed to start attack', 'danger');
        }
    }

    async stopAttack() {
        try {
            const response = await fetch('/api/attack/stop', {
                method: 'POST'
            });

            const result = await response.json();

            if (response.ok) {
                this.showAlert('All attacks stopped', 'warning');
                this.clearProgressDisplay();
            } else {
                this.showAlert(result.error || 'Failed to stop attacks', 'danger');
            }
        } catch (error) {
            console.error('Attack stop error:', error);
            this.showAlert('Failed to stop attacks', 'danger');
        }
    }

    async sendAIQuery() {
        const query = document.getElementById('ai-query')?.value || '';
        const provider = document.getElementById('ai-provider')?.value || 'auto';

        if (!query.trim()) {
            this.showAlert('Please enter an AI query', 'warning');
            return;
        }

        try {
            const response = await fetch('/api/ai/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    provider: provider
                })
            });

            const result = await response.json();

            if (response.ok) {
                this.displayAIResponse(result);
                document.getElementById('ai-query').value = ''; // Clear input
            } else {
                this.showAlert(result.error || 'AI query failed', 'danger');
            }
        } catch (error) {
            console.error('AI query error:', error);
            this.showAlert('AI query failed', 'danger');
        }
    }

    displayAIResponse(result) {
        const container = document.getElementById('lilith-responses');
        if (!container) return;

        const responseDiv = document.createElement('div');
        responseDiv.className = 'ai-response mb-3 p-3 bg-dark border border-info rounded';
        responseDiv.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-2">
                <strong class="text-info">LILITH Response (${result.provider})</strong>
                <small class="text-muted">${new Date(result.timestamp).toLocaleTimeString()}</small>
            </div>
            <div class="response-content">${this.escapeHtml(result.response)}</div>
        `;

        container.appendChild(responseDiv);
        container.scrollTop = container.scrollHeight;
    }

    async browserNavigate() {
        const url = document.getElementById('browser-url')?.value || '';

        if (!url) {
            this.showAlert('Please enter a URL', 'warning');
            return;
        }

        try {
            const response = await fetch('/api/browser/control', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    action: 'navigate',
                    url: url
                })
            });

            const result = await response.json();

            if (response.ok) {
                this.showAlert(`Browser navigated to: ${url}`, 'success');
                this.updateBrowserOutput(`Navigated to: ${url}`);
            } else {
                this.showAlert(result.error || 'Browser navigation failed', 'danger');
            }
        } catch (error) {
            console.error('Browser navigation error:', error);
            this.showAlert('Browser navigation failed', 'danger');
        }
    }

    async browserScreenshot() {
        try {
            const response = await fetch('/api/browser/control', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    action: 'screenshot'
                })
            });

            const result = await response.json();

            if (response.ok && result.screenshot) {
                this.showAlert('Screenshot taken', 'success');
                this.updateBrowserOutput(`Screenshot captured: ${result.screenshot.substring(0, 50)}...`);
            } else {
                this.showAlert(result.error || 'Screenshot failed', 'danger');
            }
        } catch (error) {
            console.error('Browser screenshot error:', error);
            this.showAlert('Screenshot failed', 'danger');
        }
    }

    updateBrowserOutput(message) {
        const container = document.getElementById('browser-output');
        if (!container) return;

        const outputDiv = document.createElement('div');
        outputDiv.className = 'mb-2';
        outputDiv.innerHTML = `<small class="text-muted">[${new Date().toLocaleTimeString()}]</small> ${this.escapeHtml(message)}`;

        container.appendChild(outputDiv);
        container.scrollTop = container.scrollHeight;
    }

    async startRecon() {
        const target = document.getElementById('target-input')?.value || '';
        const reconType = document.getElementById('recon-type')?.value || 'basic';

        if (!target) {
            this.showAlert('Please enter a target', 'warning');
            return;
        }

        try {
            const response = await fetch('/api/recon/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    target: target,
                    type: reconType
                })
            });

            const result = await response.json();

            if (response.ok) {
                this.showAlert(`Recon started: ${reconType} scan on ${target}`, 'success');
            } else {
                this.showAlert(result.error || 'Recon failed', 'danger');
            }
        } catch (error) {
            console.error('Recon error:', error);
            this.showAlert('Recon failed', 'danger');
        }
    }

    async generatePayload() {
        const payloadType = document.getElementById('payload-type')?.value || 'xss';
        const customCode = document.getElementById('payload-code')?.value || '';

        try {
            // This would integrate with the payload embedder
            const payload = await this.generateSamplePayload(payloadType, customCode);

            const container = document.getElementById('payload-output');
            if (container) {
                container.innerHTML = `
                    <div class="alert alert-success">
                        <strong>Generated ${payloadType.toUpperCase()} Payload:</strong>
                        <pre class="mt-2"><code>${this.escapeHtml(payload)}</code></pre>
                    </div>
                `;
            }

            this.showAlert('Payload generated successfully', 'success');
        } catch (error) {
            console.error('Payload generation error:', error);
            this.showAlert('Payload generation failed', 'danger');
        }
    }

    async generateSamplePayload(type, customCode) {
        // Sample payload generation - in real implementation, this would use the payload embedder
        const payloads = {
            xss: '<script>alert("XSS")</script>',
            sql: "'; DROP TABLE users; --",
            rce: '<?php system($_GET["cmd"]); ?>',
            file_upload: '<form action="/upload" method="post" enctype="multipart/form-data"><input type="file" name="file"><input type="submit"></form>'
        };

        return customCode || payloads[type] || 'Sample payload';
    }

    openOpenClaw() {
        window.open('http://127.0.0.1:18789/__openclaw__/canvas/', '_blank');
    }

    async emergencyStop() {
        if (confirm('Are you sure you want to emergency stop all operations?')) {
            await this.stopAttack();
            this.showAlert('Emergency stop activated', 'danger');
        }
    }

    updateProgressDisplay(mode, target) {
        const container = document.getElementById('progress-container');
        if (!container) return;

        container.innerHTML = `
            <div class="alert alert-info">
                <h5><i class="fas fa-play"></i> Active Attack</h5>
                <p class="mb-1"><strong>Mode:</strong> ${mode}</p>
                <p class="mb-1"><strong>Target:</strong> ${target}</p>
                <div class="progress mt-2">
                    <div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" style="width: 0%"></div>
                </div>
            </div>
        `;
    }

    clearProgressDisplay() {
        const container = document.getElementById('progress-container');
        if (!container) return;

        container.innerHTML = `
            <div class="alert alert-secondary">
                <i class="fas fa-info-circle"></i> No active attacks
            </div>
        `;
    }

    showAlert(message, type = 'info') {
        // Create a temporary alert
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(alertDiv);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new LuciferOSDashboard();
});

// Global functions for HTML onclick handlers
function startAttack() { window.dashboard?.startAttack(); }
function stopAttack() { window.dashboard?.stopAttack(); }
function sendAIQuery() { window.dashboard?.sendAIQuery(); }
function browserNavigate() { window.dashboard?.browserNavigate(); }
function browserScreenshot() { window.dashboard?.browserScreenshot(); }
function startRecon() { window.dashboard?.startRecon(); }
function generatePayload() { window.dashboard?.generatePayload(); }
function openOpenClaw() { window.dashboard?.openOpenClaw(); }
function emergencyStop() { window.dashboard?.emergencyStop(); }