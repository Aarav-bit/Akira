@echo off
title AKIRA AI Companion
cd /d "%~dp0"

echo Starting AKIRA...
echo.

:: Try to use the Python that has customtkinter installed
python gui_companion.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: Missing dependencies. Run:
    echo   pip install customtkinter pillow groq edge-tts pygame
    echo.
    pause
)
