@echo off
echo =========================================
echo Stock Analysis Dashboard - Setup Check
echo =========================================
echo.

REM Check Python
echo [1/5] Checking Python installation...
python --version 2>&1
if %errorlevel% neq 0 (
    echo [FAIL] Python is not installed or not in PATH
    goto :end
) else (
    echo [PASS] Python is installed
)
echo.

REM Check pip
echo [2/5] Checking pip...
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [FAIL] pip is not available
    goto :end
) else (
    echo [PASS] pip is available
)
echo.

REM Check dependencies
echo [3/5] Checking required packages...
python -c "import streamlit, pandas, yfinance, plotly, numpy, prophet" >nul 2>&1
if %errorlevel% neq 0 (
    echo [FAIL] Some required packages are missing
    echo [INFO] Run install.bat to install dependencies
    goto :end
) else (
    echo [PASS] All core packages installed
)
echo.

REM Check secrets file
echo [4/5] Checking secrets.toml...
if not exist .streamlit\secrets.toml (
    echo [FAIL] .streamlit\secrets.toml not found
    echo [INFO] Run install.bat to create the template
    goto :end
) else (
    echo [PASS] secrets.toml exists
)
echo.

REM Check for API keys in secrets
echo [5/5] Checking API key configuration...
findstr /C:"your-gemini-api-key-here" .streamlit\secrets.toml >nul 2>&1
if %errorlevel% equ 0 (
    echo [WARN] Gemini API key not configured - using placeholder
) else (
    echo [PASS] Gemini API key appears to be configured
)

findstr /C:"your-alpha-vantage-key-here" .streamlit\secrets.toml >nul 2>&1
if %errorlevel% equ 0 (
    echo [WARN] Alpha Vantage API key not configured - using placeholder
) else (
    echo [PASS] Alpha Vantage API key appears to be configured
)
echo.

echo =========================================
echo Setup Check Complete!
echo =========================================
echo.
echo Your environment appears to be ready.
echo Run start.bat to launch the dashboard.
echo.

:end
pause
