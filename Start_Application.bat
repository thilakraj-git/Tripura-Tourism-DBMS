@echo off
title Tripura Tourism Web Application Launcher
color 0A

echo ============================================================================
echo         TRIPURA TOURISM OFFICIAL SMART WEB APPLICATION LAUNCHER
echo ============================================================================
echo.
echo Starting local application server on http://127.0.0.1:8000 ...
echo.

cd /d "%~dp0"

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not found in your PATH!
    echo Please install Python 3.10+ from python.org or Microsoft Store.
    pause
    exit /b 1
)

:: Run the application server (it will automatically open your browser)
python run_server.py

pause
