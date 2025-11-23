@echo off
echo =========================================
echo Stock Analysis Dashboard - Starting...
echo =========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if dependencies are installed
python -c "import streamlit, pandas, yfinance, plotly, numpy, google.generativeai" >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Some dependencies are missing.
    echo.
    echo Please run one of the following:
    echo   - install.bat (full installation)
    echo   - quick-fix.bat (install missing packages only)
    echo.
    pause
    exit /b 1
)

REM Check if secrets.toml exists
if not exist .streamlit\secrets.toml (
    echo WARNING: .streamlit\secrets.toml not found!
    echo Please run install.bat first or create the secrets file manually.
    pause
    exit /b 1
)

echo Starting Stock Analysis Dashboard...
echo.
echo The dashboard will open in your default web browser.
echo Press Ctrl+C to stop the server.
echo.

streamlit run Home.py
