@echo off
REM Windows setup script for Claude Code Vector Memory

echo Claude Code Vector Memory - Setup
echo =================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or later from https://python.org
    exit /b 1
)

REM Check if venv exists, if not create it
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        exit /b 1
    )
)

REM Activate virtual environment and run setup
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Error: Failed to activate virtual environment
    exit /b 1
)

REM Run the Python setup script
python setup.py %*

REM Deactivate virtual environment
deactivate