#!/bin/bash
# Unix search script for Claude Code Vector Memory

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found"
    echo "Please run ./setup.sh first"
    exit 1
fi

# Activate virtual environment and run search
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Error: Failed to activate virtual environment"
    exit 1
fi

# Run the Python search script with all arguments
python search.py "$@"