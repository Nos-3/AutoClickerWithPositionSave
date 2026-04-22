@echo off
REM Build script for Windows

echo Building AutoClicker for Windows...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python not found. Please install Python 3.7 or higher.
    echo Download from: https://www.python.org/downloads/
    exit /b 1
)

REM Create virtual environment if needed
if not exist ".venv" (
    echo * Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Install dependencies
echo - Installing dependencies...
pip install -q pyautogui pynput pyinstaller

REM Build the app
echo * Building app...
pyinstaller --onefile --windowed --name="AutoClicker" autoclicker.py

echo.
echo = Build complete!
echo.
echo Location: dist\AutoClicker.exe
echo.
echo To share: Copy dist\AutoClicker.exe to anyone's Windows PC
echo To run: Double-click AutoClicker.exe
