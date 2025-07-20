#!/bin/bash
# Unified setup script for Claude Code Vector Memory System
# This script automates the entire setup process including Claude Code integration

set -e  # Exit on error

echo "🚀 Claude Code Vector Memory - Complete Setup"
echo "============================================="
echo ""

# Ensure we're in the right directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/.."

# Step 1: Python Environment Setup
echo "📦 Step 1: Setting up Python environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate
echo "✅ Virtual environment activated"

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed"

# Step 2: Download SpaCy model (if needed)
echo ""
echo "🧠 Step 2: Checking SpaCy model..."
if python -c "import spacy; spacy.load('en_core_web_sm')" 2>/dev/null; then
    echo "✅ SpaCy model already installed"
else
    echo "📥 Downloading SpaCy English model..."
    python -m spacy download en_core_web_sm
    echo "✅ SpaCy model installed"
fi

# Step 3: Initialize ChromaDB
echo ""
echo "🗃️ Step 3: Initializing ChromaDB..."
if [ ! -d "chroma_db" ]; then
    mkdir -p chroma_db
    echo "✅ ChromaDB directory created"
else
    echo "✅ ChromaDB directory already exists"
fi

# Step 4: Build initial index
echo ""
echo "📚 Step 4: Building initial memory index..."
python scripts/index_summaries.py
echo "✅ Initial index built"

# Step 5: Claude Code Integration
echo ""
echo "🔗 Step 5: Setting up Claude Code integration..."

# Create commands directory
mkdir -p ~/.claude/commands/system/

# Copy command files
cp claude-integration/commands/semantic-memory-search.md ~/.claude/commands/system/
cp claude-integration/commands/memory-health-check.md ~/.claude/commands/system/
echo "✅ Command files installed"

# Check and update CLAUDE.md
if [ -f ~/.claude/CLAUDE.md ]; then
    if grep -q "Memory Integration (MANDATORY)" ~/.claude/CLAUDE.md; then
        echo "✅ Memory Integration already configured in CLAUDE.md"
    else
        echo ""
        echo "⚠️  Memory Integration not found in CLAUDE.md"
        echo ""
        echo "Would you like to automatically add the Memory Integration section? (y/n)"
        read -r response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            # Extract just the memory integration section from the snippet
            sed -n '/## Memory Integration (MANDATORY)/,/^$/p' claude-integration/CLAUDE.md-snippet.md | sed '1d;$d' >> ~/.claude/CLAUDE.md
            echo "✅ Memory Integration added to CLAUDE.md"
        else
            echo "📖 Please manually add the Memory Integration section from:"
            echo "   claude-integration/CLAUDE.md-snippet.md"
        fi
    fi
else
    echo "⚠️  ~/.claude/CLAUDE.md not found"
    echo "📖 Creating CLAUDE.md with Memory Integration..."
    # Extract just the memory integration section
    sed -n '/## Memory Integration (MANDATORY)/,/^$/p' claude-integration/CLAUDE.md-snippet.md | sed '1d;$d' > ~/.claude/CLAUDE.md
    echo "✅ Created CLAUDE.md with Memory Integration"
fi

# Step 6: Create global search command
echo ""
echo "🌐 Step 6: Setting up global search command..."
if [ ! -f ~/agents/claude-memory-search ]; then
    cat > ~/agents/claude-memory-search << 'EOF'
#!/bin/bash
# Global semantic memory search script

MEMORY_DIR="$HOME/agents/claude-code-vector-memory"

if [ ! -d "$MEMORY_DIR" ]; then
    echo "❌ Semantic memory system not found at $MEMORY_DIR"
    exit 1
fi

if [ $# -eq 0 ]; then
    echo "Usage: claude-memory-search <search query>"
    echo "Example: claude-memory-search 'vue component implementation'"
    exit 1
fi

cd "$MEMORY_DIR"
./scripts/search.sh "$@"
EOF
    
    chmod +x ~/agents/claude-memory-search
    echo "✅ Global search script created"
else
    echo "✅ Global search script already exists"
fi

# Add to PATH if needed
if ! echo "$PATH" | grep -q "$HOME/agents"; then
    echo "🛤️  Adding ~/agents to PATH..."
    
    # Determine shell config file
    if [ -n "$ZSH_VERSION" ]; then
        SHELL_CONFIG="$HOME/.zshrc"
    elif [ -n "$BASH_VERSION" ]; then
        SHELL_CONFIG="$HOME/.bashrc"
    else
        SHELL_CONFIG="$HOME/.profile"
    fi
    
    echo "" >> "$SHELL_CONFIG"
    echo "# Add agents directory to PATH for claude-memory-search" >> "$SHELL_CONFIG"
    echo 'export PATH="$HOME/agents:$PATH"' >> "$SHELL_CONFIG"
    
    echo "✅ Added ~/agents to PATH in $SHELL_CONFIG"
    PATH_UPDATED=true
else
    echo "✅ ~/agents already in PATH"
    PATH_UPDATED=false
fi

# Step 7: Run health check
echo ""
echo "🏥 Step 7: Running system health check..."
python scripts/health_check.py

# Step 8: Test the system
echo ""
echo "🧪 Step 8: Testing the system..."
echo "Running a test search..."
python scripts/memory_search.py "test query" | head -n 20

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Index your Claude summaries: place them in claude_summaries/"
echo "2. Run: ./scripts/reindex.sh"
if [ "$PATH_UPDATED" = true ]; then
    echo "3. Restart your shell or run: source $SHELL_CONFIG"
    echo "4. Test global search: claude-memory-search 'your query'"
    echo "5. In Claude Code: /system:semantic-memory-search your query"
else
    echo "3. Test global search: claude-memory-search 'your query'"
    echo "4. In Claude Code: /system:semantic-memory-search your query"
fi
echo ""
echo "For more information, see docs/INTEGRATION.md"