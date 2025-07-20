#!/bin/bash
# Code quality checks using ruff

set -e

# Ensure we're in the right directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/.."

echo "🔍 Running code quality checks"
echo "=============================="

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found!"
    exit 1
fi

# Check if ruff is installed
if ! command -v ruff &> /dev/null; then
    echo "📦 Installing ruff..."
    pip install ruff
fi

echo ""
echo "🧹 Running ruff checks..."
ruff check scripts/ tests/ --fix

echo ""
echo "🎨 Running ruff format..."
ruff format scripts/ tests/

echo ""
echo "🔍 Running mypy type checks..."
if command -v mypy &> /dev/null; then
    mypy scripts/ --ignore-missing-imports || true
else
    echo "⚠️  mypy not installed, skipping type checks"
fi

echo ""
echo "✅ Code quality checks complete!"