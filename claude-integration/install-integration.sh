#!/bin/bash
# Install Claude Code integration for semantic memory system

set -e

echo "🔗 Installing Claude Code Integration"
echo "===================================="

# Check if we're in the right directory
if [ ! -f "search.py" ]; then
    echo "❌ Please run this script from the claude-code-vector-memory directory"
    exit 1
fi

# Create commands directory
echo "📁 Creating commands directory..."
mkdir -p ~/.claude/commands/system/

# Copy command files
echo "📄 Copying command files..."
cp claude-integration/commands/semantic-memory-search.md ~/.claude/commands/system/
cp claude-integration/commands/memory-health-check.md ~/.claude/commands/system/

echo "✅ Command files installed"

# Check if CLAUDE.md exists
if [ -f ~/.claude/CLAUDE.md ]; then
    echo "📋 CLAUDE.md found"
    
    # Check if Memory Integration already exists
    if grep -q "Memory Integration (MANDATORY)" ~/.claude/CLAUDE.md; then
        echo "✅ Memory Integration already configured in CLAUDE.md"
    else
        echo "⚠️  Memory Integration not found in CLAUDE.md"
        echo "📖 Please add the Memory Integration section from:"
        echo "   claude-integration/CLAUDE.md-snippet.md"
        echo ""
        echo "   Or run:"
        echo "   cat claude-integration/CLAUDE.md-snippet.md"
    fi
else
    echo "⚠️  ~/.claude/CLAUDE.md not found"
    echo "📖 Please create it and add the Memory Integration section from:"
    echo "   claude-integration/CLAUDE.md-snippet.md"
fi

# Install global search script
echo "🌐 Installing global search script..."
if [ -f ~/agents/claude-memory-search ]; then
    echo "✅ Global search script already exists"
else
    # Create the global search script
    cat > ~/agents/claude-memory-search << 'EOF'
#!/bin/bash
# Global semantic memory search script
# Callable from anywhere in the system

# Ensure we're using the right directory
MEMORY_DIR="$HOME/agents/claude-code-vector-memory"

if [ ! -d "$MEMORY_DIR" ]; then
    echo "❌ Semantic memory system not found at $MEMORY_DIR"
    exit 1
fi

# Check if query provided
if [ $# -eq 0 ]; then
    echo "Usage: claude-memory-search <search query>"
    echo "Example: claude-memory-search 'vue component implementation'"
    exit 1
fi

# Change to memory system directory and run search
cd "$MEMORY_DIR"
./search.sh "$@"
EOF
    
    chmod +x ~/agents/claude-memory-search
    echo "✅ Global search script created"
fi

# Add to PATH if not already there
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
    
    # Add to PATH
    echo "" >> "$SHELL_CONFIG"
    echo "# Add agents directory to PATH for claude-memory-search" >> "$SHELL_CONFIG"
    echo 'export PATH="$HOME/agents:$PATH"' >> "$SHELL_CONFIG"
    
    echo "✅ Added ~/agents to PATH in $SHELL_CONFIG"
    echo "🔄 Please restart your shell or run: source $SHELL_CONFIG"
else
    echo "✅ ~/agents already in PATH"
fi

# Test installation
echo "🧪 Testing installation..."

# Test command files
if [ -f ~/.claude/commands/system/semantic-memory-search.md ]; then
    echo "✅ semantic-memory-search command installed"
else
    echo "❌ semantic-memory-search command not found"
fi

if [ -f ~/.claude/commands/system/memory-health-check.md ]; then
    echo "✅ memory-health-check command installed"
else
    echo "❌ memory-health-check command not found"
fi

# Test global search
if [ -x ~/agents/claude-memory-search ]; then
    echo "✅ Global search script executable"
else
    echo "❌ Global search script not executable"
fi

echo ""
echo "🎉 Integration installation complete!"
echo ""
echo "Next steps:"
echo "1. Add Memory Integration section to ~/.claude/CLAUDE.md (see claude-integration/CLAUDE.md-snippet.md)"
echo "2. Restart your shell or run: source ~/.bashrc (or ~/.zshrc)"
echo "3. Test with: claude-memory-search 'test query' or ./search.sh 'test query'"
echo "4. In Claude Code, try: /system:semantic-memory-search test query"
echo ""
echo "For help, see docs/INTEGRATION.md"