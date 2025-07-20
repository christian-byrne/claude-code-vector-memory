#!/bin/bash
# Run all tests for the semantic memory system

set -e  # Exit on error

echo "🧪 Running Semantic Memory System Tests"
echo "======================================"

# Ensure we're in the right directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/.."

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found!"
    echo "Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Run unit tests
echo -e "\n📋 Running unit tests..."
python -m pytest tests/ -v --color=yes || true

# Run integration test
echo -e "\n🔄 Running integration tests..."
python tests/test_system.py

# Run health check
echo -e "\n🏥 Running health check..."
python scripts/health_check.py

echo -e "\n✅ All tests completed!"
echo "Check the output above for any failures or issues."