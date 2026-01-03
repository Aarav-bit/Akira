@echo off
echo Starting AI Voice Chatbot...
echo.

REM Check if .env exists
if not exist .env (
    echo ERROR: .env file not found!
    echo.
    echo Please create a .env file with your GROQ_API_KEY:
    echo GROQ_API_KEY=your_api_key_here
    echo.
    pause
    exit /b 1
)

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Install/update dependencies
echo Installing dependencies...
echo.
echo Note: PyAudio may need special installation on Windows.
echo If installation fails, run: pip install pipwin && pipwin install pyaudio
echo.
pip install -r requirements.txt --quiet

REM Run the chatbot
echo.
python main.py

pause

