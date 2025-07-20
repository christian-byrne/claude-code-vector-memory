# Semantic Memory System for Claude Code

Give Claude persistent memory across conversations by indexing and searching your session summaries.

## 🚀 Quick Start

### One-Command Setup

```bash
git clone <this-repo>
cd claude-code-vector-memory

# Complete setup with Claude Code integration
./scripts/setup-all.sh  # Linux/macOS
python setup-all.py     # Windows

# Basic setup only
./scripts/setup.sh      # Linux/macOS  
python setup.py         # Windows
```

The complete setup automatically:
✅ Creates Python environment  
✅ Installs dependencies  
✅ Sets up Claude Code integration  
✅ Creates global search command  
✅ Runs health checks  

### Start Searching

```bash
# From anywhere (after setup)
claude-memory-search "vue component implementation"

# From this directory
./scripts/search.sh "your query"    # Linux/macOS
python search.py "your query"       # Windows

# In Claude Code
/system:semantic-memory-search your query
```

### Add Your Summaries

1. Place summary files in `claude_summaries/`
2. Run: `./scripts/reindex.sh` (Linux/macOS) or `python scripts/index_summaries.py` (Windows)

## Features

- **Semantic Search**: Uses sentence transformers to find conceptually similar past sessions
- **Hybrid Scoring**: Combines semantic similarity (70%), recency (20%), and complexity (10%)
- **Rich Metadata**: Extracts titles, dates, technologies, file paths, and more
- **ChromaDB Backend**: Fast vector similarity search with persistent storage
- **Beautiful CLI**: Rich terminal output with tables and formatted results
- **Cross-Platform**: Works on Linux, macOS, and Windows
- **Claude Code Integration**: Automatic memory search before every task

## Installation

1. Ensure you're in the claude-code-vector-memory directory
2. Run the complete setup (recommended):
   ```bash
   ./scripts/setup-all.sh
   ```
   This will:
   - Create virtual environment
   - Install all dependencies
   - Build initial index
   - Set up Claude Code integration
   - Create global search command
   - Run health check
   
   Or for basic setup only:
   ```bash
   ./scripts/setup.sh
   ```

3. Core dependencies installed:
   - sentence-transformers (embeddings)
   - chromadb (vector storage)
   - rich (terminal UI)
   - PyYAML (configuration)

## Usage

### 1. Index Your Summaries (First Time)

```bash
python scripts/index_summaries.py
```

This scans `~/.claude/compacted-summaries/` and creates embeddings for each summary.

### 2. Search for Past Sessions

```bash
python scripts/memory_search.py "vue widget implementation"
```

Returns the top 3 most relevant past sessions with:
- Similarity scores
- Brief previews
- File paths to full summaries

### 3. Analyze Metadata

```bash
python scripts/extract_metadata.py
```

Shows what information can be extracted from your summaries.

### 4. Test Everything

```bash
python tests/test_system.py
```

Runs through all components to verify the system works correctly.

## How It Works

1. **Indexing**: 
   - Reads all markdown files from `~/.claude/compacted-summaries/`
   - Extracts metadata (title, date, technologies, etc.)
   - Generates embeddings using `all-MiniLM-L6-v2` model
   - Stores in ChromaDB with metadata

2. **Searching**:
   - Converts query to embedding
   - Finds nearest neighbors in vector space
   - Calculates hybrid score with recency weighting
   - Returns top results above similarity threshold

3. **Scoring Algorithm**:
   ```
   hybrid_score = (0.7 × semantic_similarity) + 
                  (0.2 × recency_score) + 
                  (0.1 × complexity_bonus)
   ```

## Integration with Claude Code

The system is now fully integrated with Claude Code:

### 1. Automatic Memory Search
Claude Code will automatically search for relevant past work before starting new tasks. This is configured in `~/.claude/CLAUDE.md`.

### 2. Manual Memory Search Command
Use the command: `/system:semantic-memory-search <your task description>`

### 3. Health Check Command
Use the command: `/system:memory-health-check`

### 4. Enhanced Summary Generation
New summaries now include rich metadata for better search. Use:
`/project:AGENT-summarize-and-log-current-session-v2`

### Shell Scripts

- `./scripts/setup.sh` - Initial setup and configuration
- `./scripts/search.sh <query>` - Quick search interface
- `./scripts/reindex.sh` - Rebuild the entire index (with backup)
- `./scripts/run_tests.sh` - Run all tests and health checks

### Python Scripts

- `scripts/index_summaries.py` - Index summaries into ChromaDB
- `scripts/memory_search.py` - Semantic search functionality
- `scripts/health_check.py` - System diagnostics and reporting
- `scripts/extract_metadata.py` - Metadata analysis tools

### Testing

Run the test suite with:
```bash
./scripts/run_tests.sh
```

Or run specific tests:
```bash
python -m pytest tests/test_metadata_extraction.py -v
python -m pytest tests/test_search_functionality.py -v
```

## Database Location

The vector database is stored at:
```
claude-code-vector-memory/chroma_db/
```

This persists between sessions, so you only need to index new summaries.

## Extending the System

- **Add more metadata**: Edit `extract_metadata()` in index_summaries.py
- **Adjust scoring**: Modify weights in `search()` method
- **Change embedding model**: Update `EMBEDDING_MODEL` constant
- **Filter by project**: Add project-based filtering to search