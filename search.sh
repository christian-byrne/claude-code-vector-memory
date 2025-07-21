#!/bin/bash
# Unix search script for Claude Code Vector Memory

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if venv exists in the script's directory
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "Error: Virtual environment not found"
    echo "Please run ./setup.sh first"
    exit 1
fi

# Run using the venv Python directly (more reliable than activation)
# This works regardless of shell environment or pyenv
"$SCRIPT_DIR/venv/bin/python" "$SCRIPT_DIR/search.py" "$@"