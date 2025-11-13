@echo off
echo =========================================
echo Stock Analysis Dashboard - Installation
echo =========================================
echo.

echo Checking Python version...
python -c "import sys; sys.exit(1) if not (sys.version_info.major == 3 and 10 <= sys.version_info.minor < 14) else sys.exit(0)"
if %errorlevel% neq 0 (
    echo ERROR: This script requires Python version 3.10, 3.11, 3.12, or 3.13.
    echo Your current version is:
    python --version
    echo Please install a compatible Python version and ensure it's in your PATH.
    pause
    exit /b 1
)

echo Checking for pip...
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: pip is not available. Please ensure you have a working Python installation with pip.
    pause
    exit /b 1
)

echo Step 1: Installing Python dependencies...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Step 2: Downloading NLTK data...
python -c "import nltk; nltk.download('vader_lexicon'); nltk.download('punkt')"
if %errorlevel% neq 0 (
    echo WARNING: NLTK data download failed, but continuing...
)

echo.
echo Step 3: Creating .streamlit directory and secrets.toml template...
if not exist .streamlit (
    mkdir .streamlit
)

(
    echo # Google Gemini API Key - Get from https://makersuite.google.com/app/apikey
    echo GOOGLE_API_KEY = "your-gemini-api-key-here"
    echo.
    echo # Alpha Vantage API Key - Get from https://www.alpha-vantage.co/support/#api-key
    echo [alpha_vantage]
    echo api_key = "your-alpha-vantage-key-here"
) > .streamlit\secrets.toml

echo.
echo =========================================
echo Installation Complete!
echo =========================================
echo.
echo NEXT STEPS:
echo 1. IMPORTANT: Edit the newly created .streamlit\secrets.toml file and add your API keys.
echo.
echo 2. Run the application:
echo    streamlit run dashboard.py
echo.
echo See SETUP_GUIDE.md for detailed instructions.
echo.
pause
