# Stock Analysis Dashboard - Startup Guide

## Quick Start

### First Time Setup
1. Run `install.bat` - Installs all dependencies and creates secrets template
2. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and fill your API keys.
  **Important:** `.streamlit/secrets.toml` is git-ignored - never commit it.
3. Run `start.bat` - Launches the dashboard

### Daily Use
- **start.bat** - Normal startup (recommended)
- **start-dev.bat** - Development mode with auto-reload and debug logging
- **start-no-browser.bat** - Starts without opening browser (access at http://localhost:8501)

## Available Batch Files

### install.bat
- **Purpose**: First-time installation
- **What it does**:
  - Validates Python version (3.10-3.13)
  - Installs all Python dependencies from requirements.txt
  - Downloads required NLTK data
  - Creates `.streamlit/secrets.toml` template
- **When to use**: First time setting up the project

### start.bat
- **Purpose**: Normal application startup
- **What it does**:
  - Validates Python and dependencies
  - Checks for secrets.toml
  - Launches Streamlit dashboard
- **When to use**: Daily use, production mode

### start-dev.bat
- **Purpose**: Development mode startup
- **Features**:
  - Auto-reload on file changes
  - Debug logging enabled
  - Browser auto-opens
- **When to use**: When developing/debugging

### start-no-browser.bat
- **Purpose**: Headless startup
- **Features**:
  - Starts server without opening browser
  - Access manually at http://localhost:8501
- **When to use**: Remote servers, testing, or when you prefer manual browser control

### update.bat
- **Purpose**: Update dependencies
- **What it does**:
  - Upgrades pip to latest version
  - Updates all packages from requirements.txt
- **When to use**: After requirements.txt changes or periodic maintenance

### quick-fix.bat
- **Purpose**: Quick fix for missing packages
- **What it does**:
  - Installs commonly missing packages (like google-generativeai)
  - Faster than running full install.bat
- **When to use**: When you get "ModuleNotFoundError" for specific packages

### check-setup.bat
- **Purpose**: Validate environment setup
- **What it does**:
  - Checks Python installation
  - Verifies all dependencies
  - Validates secrets.toml exists and is configured
  - Reports any issues
- **When to use**: Troubleshooting, after installation, before major updates

## Troubleshooting

### "Python is not installed or not in PATH"
- Install Python 3.10-3.13 from python.org
- Ensure "Add to PATH" is checked during installation
- Restart your terminal/command prompt

### "Dependencies not installed"
- Run `install.bat` to install all required packages
- If errors occur, try running as administrator

### "secrets.toml not found"
- Run `install.bat` to create the template
- Manually create or copy `.streamlit/secrets.toml` (from `.streamlit/secrets.toml.example`) and add your API keys. Do not commit this file.

### Dashboard won't start
1. Run `check-setup.bat` to diagnose issues
2. Verify all checks pass
3. Check if port 8501 is already in use
4. Try `start-no-browser.bat` to see detailed error messages

## Port Configuration

By default, Streamlit runs on port 8501. To change:
```bash
streamlit run dashboard.py --server.port 8502
```

## Stopping the Server

Press `Ctrl+C` in the terminal window where the server is running.

## API Keys Required

### Google Gemini API
- Get from: https://makersuite.google.com/app/apikey
- Used for: AI-powered analysis features

### Alpha Vantage API
- Get from: https://www.alpha-vantage.co/support/#api-key
- Used for: Additional stock data and fundamentals

Configure these in `.streamlit\secrets.toml` after running install.bat.
