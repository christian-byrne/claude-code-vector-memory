#!/bin/bash
# Initial setup for the semantic memory system

set -e

echo "🚀 Setting up Semantic Memory System"
echo "===================================="

# Ensure we're in the right directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
source venv/bin/activate
echo "✅ Virtual environment activated"

# Install dependencies
echo -e "\n📚 Installing dependencies..."
pip install --upgrade pip
pip install sentence-transformers chromadb rich spacy pytest

# Download spacy model
echo -e "\n🌐 Downloading spaCy language model..."
python -m spacy download en_core_web_sm || true

# Create requirements.txt
echo -e "\n📄 Creating requirements.txt..."
pip freeze > requirements.txt
echo "✅ requirements.txt created"

# Make scripts executable
echo -e "\n🔧 Making scripts executable..."
chmod +x scripts/*.py
chmod +x *.sh
chmod +x test_system.py
echo "✅ Scripts are now executable"

# Initial indexing
echo -e "\n🔨 Building initial index..."
python scripts/index_summaries.py

# Run health check
echo -e "\n🏥 Running health check..."
python scripts/health_check.py

echo -e "\n✅ Setup completed!"
echo ""
echo "You can now use:"
echo "  ./search.sh 'your search query'    - Search memories"
echo "  ./run_tests.sh                     - Run all tests"
echo "  ./reindex.sh                       - Rebuild the index"
echo ""
echo "Or use the Python scripts directly:"
echo "  python scripts/memory_search.py 'query'"
echo "  python scripts/health_check.py"