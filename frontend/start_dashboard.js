/**
 * LuciferOS Dashboard Launcher
 * Starts the Python Flask backend and dashboard
 */
const { spawn } = require('child_process');
const path = require('path');

const appDir = path.join(__dirname, '..');
const backendPath = path.join(appDir, 'tools', 'lilith_full_backend.py');
const dashboardPath = path.join(appDir, 'ui', 'web_dashboard_master.py');
const pythonPath = '/root/.venv/bin/python3';

console.log('Starting LuciferOS System...');

// Start Flask backend first
console.log('1. Starting LILITH Backend on port 5000...');
const backend = spawn(pythonPath, [backendPath], {
    env: {
        ...process.env,
        BACKEND_HOST: '0.0.0.0',
        BACKEND_PORT: '5000'
    },
    cwd: appDir,
    stdio: 'inherit'
});

backend.on('error', (err) => {
    console.error('Failed to start backend:', err);
});

// Wait a bit then start dashboard
setTimeout(() => {
    console.log('2. Starting Web Dashboard on port 3000...');
    const dashboard = spawn(pythonPath, [dashboardPath], {
        env: {
            ...process.env,
            WEB_DASHBOARD_PORT: '3000',
            WEB_DASHBOARD_HOST: '0.0.0.0'
        },
        cwd: appDir,
        stdio: 'inherit'
    });

    dashboard.on('error', (err) => {
        console.error('Failed to start dashboard:', err);
        process.exit(1);
    });

    dashboard.on('exit', (code) => {
        console.log('Dashboard exited with code:', code);
        backend.kill('SIGTERM');
        process.exit(code);
    });

    // Keep process running
    process.on('SIGTERM', () => {
        dashboard.kill('SIGTERM');
        backend.kill('SIGTERM');
    });

    process.on('SIGINT', () => {
        dashboard.kill('SIGINT');
        backend.kill('SIGINT');
    });
}, 3000);
