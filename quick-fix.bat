@echo off
echo =========================================
echo Quick Fix - Installing Missing Package
echo =========================================
echo.

echo Installing google-generativeai package...
python -m pip install google-generativeai

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to install google-generativeai
    echo.
    echo Try running: pip install google-generativeai
    pause
    exit /b 1
)

echo.
echo =========================================
echo Package Installed Successfully!
echo =========================================
echo.
echo The missing package has been installed.
echo You can now restart the dashboard.
echo.
pause
