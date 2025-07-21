@echo off
REM Windows search script for Claude Code Vector Memory

REM Check if venv exists
if not exist "venv\" (
    echo Error: Virtual environment not found
    echo Please run setup.bat first
    exit /b 1
)

REM Activate virtual environment and run search
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Error: Failed to activate virtual environment
    exit /b 1
)

REM Run the Python search script with all arguments
python search.py %*

REM Deactivate virtual environment
deactivate