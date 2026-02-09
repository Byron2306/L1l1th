# LuciferOS - Product Requirements Document

## Original Problem Statement
Build a complex red-teaming platform called "LuciferOS" with:
- Web dashboard for LILITH AI Attack Assistant
- Backend services for AI-powered security testing
- API key harvesting system with Playwright automation
- Integration with OpenClaw framework
- 15+ advanced red-teaming capabilities
- CAPTCHA bypass system
- Offensive security tools integration
- Enhanced ML anomaly detection

## Current Architecture

### Services
- **Port 3000**: Flask Web Dashboard (`ui/web_dashboard_master.py`)
- **Port 5000**: LILITH Backend (`tools/lilith_full_backend.py`)  
- **Port 8001**: FastAPI Proxy (`backend/server.py`)

### Key Files
- `/app/ui/web_dashboard_master.py` - Main dashboard UI with all tabs
- `/app/tools/lilith_full_backend.py` - Core backend logic with all endpoints
- `/app/tools/playwright_harvester.py` - Real Playwright-based browser automation
- `/app/tools/captcha_bypass.py` - Multi-method CAPTCHA bypass system
- `/app/tools/offensive_tools.py` - Security tools integration (Nmap, SQLMap, etc.)
- `/app/tools/ml_anomaly_detection.py` - Enhanced ML models
- `/app/tools/advanced_capabilities.py` - 15 advanced red-team capabilities
- `/app/tools/harvest_integration.py` - Harvester backend endpoints

## What's Been Implemented (Feb 9, 2026)

### ✅ CAPTCHA Bypass System (`/app/tools/captcha_bypass.py`)
- **2Captcha/Anti-Captcha API Integration** - External solving service
- **Local ML-based OCR** - OpenCV + pytesseract for simple CAPTCHAs
- **reCAPTCHA v2/v3 bypass** - Token harvesting techniques
- **hCaptcha bypass** - Accessibility cookie methods
- **Cloudflare challenge bypass** - FlareSolverr, undetected-chromedriver
- **Audio CAPTCHA solver** - Speech recognition
- **Text CAPTCHA solver** - Pattern matching for math/logic questions
- **Enhanced browser automation** - Stealth mode, human-like interactions

### ✅ Offensive Security Tools (`/app/tools/offensive_tools.py`)
- **NmapScanner** - Quick/full/vuln/OS scans
- **SQLMapScanner** - SQL injection testing
- **WebVulnScanner** - Nikto/Nuclei integration
- **DirectoryBruter** - Gobuster/ffuf/dirb
- **PasswordCracker** - Hydra/John integration
- **ToolManager** - Check/install security tools

### ✅ Enhanced ML Models (`/app/tools/ml_anomaly_detection.py`)
- **IsolationForestDetector** - Outlier detection
- **LOFDetector** - Local Outlier Factor
- **ClusteringDetector** - DBSCAN/KMeans clustering
- **StatisticalDetector** - Z-score, IQR methods
- **TimeSeriesDetector** - Rolling window anomalies
- **ThreatPredictor** - Random Forest classification
- **FeatureExtractor** - Network/User/Log feature extraction
- **EnhancedAnomalyDetector** - Combined multi-method detection

### ✅ Dashboard UI Updates
- New "Advanced" tab with 15 capability modules
- Offensive Tools panel (Nmap, SQLMap, DirBrute)
- ML Analysis panel (Events, Time Series)
- CAPTCHA Bypass panel (reCAPTCHA, hCaptcha, Cloudflare)

## API Endpoints

### CAPTCHA Endpoints
- `POST /captcha/solve` - Solve CAPTCHA
- `GET /captcha/stats` - Solving statistics

### Offensive Tools Endpoints
- `GET /offensive/status` - Tool availability
- `POST /offensive/nmap/quick|full|vuln` - Nmap scans
- `POST /offensive/sqlmap/test` - SQL injection test
- `POST /offensive/web/scan` - Web vulnerability scan
- `POST /offensive/dirs/brute` - Directory brute force
- `POST /offensive/password/brute` - Password brute force
- `POST /offensive/password/crack` - Hash cracking
- `POST /offensive/full-scan` - Comprehensive scan

### Enhanced ML Endpoints
- `POST /ml/train` - Train all models
- `POST /ml/detect` - Detect anomalies
- `POST /ml/analyze-events` - Security event analysis
- `POST /ml/time-series` - Time series anomaly detection
- `POST /ml/predict-threat` - Threat prediction

## Test Results (Feb 9, 2026)
- ✅ CAPTCHA bypass: 3 Cloudflare techniques available
- ✅ ML time series: Detected 1 anomaly in test data
- ✅ Dashboard: Backend status OK
- ✅ All services running via supervisor

## Known Limitations
- Nmap/SQLMap/Nikto not installed (simulated mode)
- 2Captcha API key required for external solving
- Preview URL shows "Unavailable" when session idle

## Files Created This Session
- `/app/tools/captcha_bypass.py` - NEW
- `/app/tools/offensive_tools.py` - NEW  
- `/app/tools/ml_anomaly_detection.py` - NEW
- `/app/tools/playwright_harvester.py` - NEW
- `/app/tools/advanced_capabilities.py` - REWRITTEN
- `/app/tools/harvest_integration.py` - UPDATED

## Next Steps
1. Install actual security tools (nmap, nikto, sqlmap)
2. Add 2Captcha API key for real CAPTCHA solving
3. Implement real browser automation for provider signups
4. Add more AI providers to harvester
