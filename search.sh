#!/bin/bash
# Unix search script for Claude Code Vector Memory

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found"
    echo "Please run ./setup.sh first"
    exit 1
fi

# Run using the venv Python directly (more reliable than activation)
# This works regardless of shell environment or pyenv
venv/bin/python search.py "$@"