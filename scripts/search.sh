#!/bin/bash
# Quick semantic search interface

set -e

# Ensure we're in the right directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/.."

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "❌ Virtual environment not found!"
    exit 1
fi

# Check if query provided
if [ $# -eq 0 ]; then
    echo "Usage: ./scripts/search.sh <search query>"
    echo "Example: ./scripts/search.sh 'vue component implementation'"
    exit 1
fi

# Run search using venv python directly
if [ -f "venv/bin/python" ]; then
    venv/bin/python scripts/memory_search.py "$@"
elif [ -f "venv/bin/python3" ]; then
    venv/bin/python3 scripts/memory_search.py "$@"
else
    echo "Error: No python interpreter found in virtual environment"
    exit 1
fi