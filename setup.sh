#!/bin/bash
# Unix setup script for Claude Code Vector Memory

echo "Claude Code Vector Memory - Setup"
echo "================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.8 or later"
    exit 1
fi

# Check if venv exists, if not create it
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment"
        exit 1
    fi
fi

# Run setup using the venv Python directly (more reliable than activation)
# This works regardless of shell environment or pyenv
venv/bin/python setup.py "$@"