@echo off
echo =========================================
echo Stock Analysis Dashboard - Update
echo =========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo Updating Python dependencies...
echo.

python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo ERROR: Failed to upgrade pip
    pause
    exit /b 1
)

python -m pip install --upgrade -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to update dependencies
    pause
    exit /b 1
)

echo.
echo =========================================
echo Update Complete!
echo =========================================
echo.
echo All dependencies have been updated.
echo You can now run start.bat to launch the dashboard.
echo.
pause
