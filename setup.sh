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

# Activate virtual environment and run setup
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Error: Failed to activate virtual environment"
    exit 1
fi

# Run the Python setup script
python3 setup.py "$@"

# Note: We don't deactivate because the user might want to continue using the venv