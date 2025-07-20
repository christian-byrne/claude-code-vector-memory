#!/bin/bash
# Reindex all summaries in the semantic memory system

set -e

echo "🔄 Reindexing Semantic Memory System"
echo "===================================="

# Ensure we're in the right directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/.."

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found!"
    exit 1
fi

# Confirm with user
echo -e "\n⚠️  This will rebuild the entire vector database."
echo "Current database will be backed up first."
read -p "Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

# Backup existing database
if [ -d "chroma_db" ]; then
    BACKUP_NAME="chroma_db_backup_$(date +%Y%m%d_%H%M%S)"
    echo "📦 Creating backup: $BACKUP_NAME"
    cp -r chroma_db "$BACKUP_NAME"
    echo "✅ Backup created"
fi

# Run indexing
echo -e "\n🔨 Rebuilding index..."
python scripts/index_summaries.py

# Run health check
echo -e "\n🏥 Running health check..."
python scripts/health_check.py

echo -e "\n✅ Reindexing completed!"