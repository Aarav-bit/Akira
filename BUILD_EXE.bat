@echo off
title AKIRA EXE Builder
cd /d "%~dp0"

echo Building AKIRA Executable...
echo This may take a few minutes depending on your system.
echo.

:: Build command
:: --noconsole: Hide the terminal window
:: --onefile: Bundle into a single EXE (Optional, --onedir is faster to launch)
:: --add-data: Include assets folder
:: --collect-all: Ensure customtkinter themes/files are included
pyinstaller --noconsole ^
            --name "Akira" ^
            --add-data "assets;assets" ^
            --collect-all customtkinter ^
            --hidden-import PIL._tkinter_finder ^
            gui_companion.py

echo.
if %ERRORLEVEL% eq 0 (
    echo ✅ SUCCESS! Your app is in the 'dist' folder.
    echo ℹ️  Note: Remember to copy your .env file to the 'dist/Akira' folder.
) else (
    echo ❌ FAILED! Make sure pyinstaller is installed.
)
pause
