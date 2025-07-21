# Claude Code Integration Guide

This guide explains how to integrate claude-code-vector-memory with Claude Code for automatic memory functionality.

## Overview

The integration enables Claude Code to automatically search through your previous session summaries before starting new tasks, providing continuity across conversations.

## Installation

### Automatic Integration

The setup script handles most integration automatically:

```bash
cd ~/agents/claude-code-vector-memory
./setup.sh  # On Linux/macOS
setup.bat   # On Windows
```

This will:
1. Set up the vector memory system
2. Create necessary directories
3. Install Python dependencies
4. Build initial index of your summaries

### Manual Integration Steps

If you need to set up integration manually:

#### 1. Copy Command Files

```bash
# Create commands directory if it doesn't exist
mkdir -p ~/.claude/commands/system/

# Copy command files (when available)
cp claude-integration/commands/semantic-memory-search.md ~/.claude/commands/system/
cp claude-integration/commands/memory-health-check.md ~/.claude/commands/system/
```

#### 2. Update CLAUDE.md

Add the Memory Integration section to your `~/.claude/CLAUDE.md`:

```markdown
## Memory Integration (MANDATORY)

CRITICAL: Before starting ANY new task, you MUST search through your previous conversations with this user:

1. **Extract key terms** from the user's request (technologies, components, concepts)
2. **Run semantic search**: `~/agents/claude-code-vector-memory/search.sh "extracted key terms"`
3. **Review results** and identify relevant past work
4. **Present memory recap** to user showing what related work you've done before
5. **Ask user** if they want to build on previous approaches or start fresh

This is MANDATORY for all tasks, not optional. Users rely on this continuity.

When presenting found memories:
- Show a brief "memory recap" before beginning work:
  ```
  📚 I found relevant past work:
  1. [Title] - [Date]: We worked on [brief description]
     - Relevant because: [specific connection to current task]
  2. [Title] - [Date]: We implemented [solution]
     - Could apply here for: [specific aspect]
  ```
- Ask: "Would you like me to build on any of these previous approaches, or should we start fresh?"
```

#### 3. Make Global Search Available

```bash
# Copy global search script to somewhere in PATH
sudo cp ~/agents/claude-memory-search /usr/local/bin/
# Or create a symlink
ln -s ~/agents/claude-memory-search ~/.local/bin/claude-memory-search
```

## Usage

### Automatic Memory Search

Once integrated, Claude Code will automatically:
1. Extract key terms from your requests
2. Search through past sessions
3. Present relevant memories before starting work
4. Ask if you want to build on previous approaches

### Manual Commands

#### Search Memory
```
/system:semantic-memory-search vue component implementation
```

#### Health Check
```
/system:memory-health-check
```

### Direct Shell Usage

```bash
# From anywhere in the system
claude-memory-search "search terms"

# Or from the project directory
cd ~/agents/claude-code-vector-memory
./search.sh "search terms"  # On Linux/macOS
search.bat "search terms"   # On Windows
```

## Configuration

### Search Settings

Edit `scripts/memory_search.py` to adjust:

```python
# Similarity threshold (0.0 to 1.0)
SIMILARITY_THRESHOLD = 0.30

# Number of results to return
MAX_RESULTS = 3

# Hybrid scoring weights
SEMANTIC_WEIGHT = 0.7
RECENCY_WEIGHT = 0.2
COMPLEXITY_WEIGHT = 0.1
```

### Indexing Settings

Edit `scripts/index_summaries.py` to customize:

```python
# Summary source directory
SUMMARIES_DIR = Path.home() / ".claude" / "compacted-summaries"

# Embedding model
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Database location
DB_PATH = Path(__file__).parent.parent / "chroma_db"
```

## Workflow Integration

### Pre-Task Memory Search

When Claude Code starts a new task:
1. **Extract concepts** from your request
2. **Search memories** using semantic similarity
3. **Present findings** with relevance explanations
4. **Ask for direction** on building upon past work

### Post-Task Summary Enhancement

To improve future memory searches:
1. Use enhanced summary generation
2. Include YAML frontmatter with metadata
3. Specify technologies, complexity, patterns used
4. Note key files and decisions made

### Example Workflow

```
User: "Help me implement a Vue component for user authentication"

Claude: 
📚 I found relevant past work:
1. Vue Widget Implementation - 2025-06-29: We created 15 Vue widgets with reactive state
   - Relevant because: Similar component architecture and Vue patterns
2. Authentication System Setup - 2025-06-15: We implemented JWT auth with login forms
   - Could apply here for: Authentication logic and form validation

Would you like me to build on the Vue widget patterns from the first session, 
or the authentication patterns from the second, or start fresh?

User: "Use the Vue widget patterns"

Claude: [Proceeds with implementation using established patterns]
```

## Troubleshooting Integration

### Memory Search Not Working

1. **Check installation**:
   ```bash
   cd ~/agents/claude-code-vector-memory
   python scripts/health_check.py
   ```

2. **Verify database**:
   ```bash
   ./search.sh "test query"
   ```

3. **Rebuild index**:
   ```bash
   python reindex.py
   ```

### Commands Not Found

1. **Check command files exist**:
   ```bash
   ls ~/.claude/commands/system/
   ```

2. **Verify CLAUDE.md integration**:
   ```bash
   grep -A5 "Memory Integration" ~/.claude/CLAUDE.md
   ```

### Low Quality Results

1. **Check similarity threshold**:
   - Lower threshold in `memory_search.py` for more results
   - Higher threshold for more relevant results

2. **Improve summary quality**:
   - Add more descriptive YAML frontmatter
   - Include technology tags and complexity levels
   - Use semantic descriptions of what was accomplished

3. **Rebuild with better metadata**:
   ```bash
   python scripts/add_metadata_to_summaries.py
   python reindex.py
   ```

## Advanced Integration

### Custom Embedding Models

To use a different embedding model:

1. **Update configuration**:
   ```python
   EMBEDDING_MODEL = "your-preferred-model"
   ```

2. **Rebuild index**:
   ```bash
   python reindex.py
   ```

3. **Test performance**:
   ```bash
   python scripts/health_check.py
   ```

### Multiple Project Support

For project-specific memory:

1. **Add project filtering** to search logic
2. **Extend metadata** with project identifiers
3. **Create project-specific search commands**

### Integration with Other Tools

The system can integrate with:
- **Git hooks**: Auto-index commit messages
- **Documentation tools**: Index project documentation
- **Code analysis**: Include code complexity metrics
- **Time tracking**: Weight results by time spent

## Validation

After integration, verify everything works:

```bash
# Run full health check
python ~/agents/claude-code-vector-memory/scripts/health_check.py

# Test search functionality
~/agents/claude-code-vector-memory/scripts/search.sh "test search"

# Verify Claude Code can access commands
# (Start Claude Code session and try /system:semantic-memory-search)
```

## Support

If you encounter issues:
1. Check the health report output
2. Review logs in the project directory
3. Consult the troubleshooting section
4. File an issue on GitHub with environment details