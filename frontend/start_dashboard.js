/**
 * LuciferOS Dashboard Launcher
 * Starts the Python Flask dashboard on port 3000
 */
const { spawn } = require('child_process');
const path = require('path');

// Start the Flask dashboard
const dashboardPath = path.join(__dirname, '..', 'ui', 'web_dashboard_master.py');

console.log('Starting LuciferOS Dashboard...');
console.log('Dashboard path:', dashboardPath);

// Start Flask dashboard
const dashboard = spawn('python3', [dashboardPath], {
    env: {
        ...process.env,
        WEB_DASHBOARD_PORT: '3000',
        WEB_DASHBOARD_HOST: '0.0.0.0'
    },
    cwd: path.join(__dirname, '..'),
    stdio: 'inherit'
});

dashboard.on('error', (err) => {
    console.error('Failed to start dashboard:', err);
    process.exit(1);
});

dashboard.on('exit', (code) => {
    console.log('Dashboard exited with code:', code);
    process.exit(code);
});

// Keep process running
process.on('SIGTERM', () => {
    dashboard.kill('SIGTERM');
});

process.on('SIGINT', () => {
    dashboard.kill('SIGINT');
});
