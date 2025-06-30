# Semantic Memory System for Claude Code

A semantic search system that indexes Claude Code session summaries to provide persistent memory and context across conversations.

## Features

- **Semantic Search**: Uses sentence transformers to find conceptually similar past sessions
- **Hybrid Scoring**: Combines semantic similarity (70%), recency (20%), and complexity (10%)
- **Rich Metadata**: Extracts titles, dates, technologies, file paths, and more
- **ChromaDB Backend**: Fast vector similarity search with persistent storage
- **Beautiful CLI**: Rich terminal output with tables and formatted results
- **Health Monitoring**: Built-in diagnostics and quality checks
- **Unit Tests**: Comprehensive test coverage for reliability

## Quick Start

```bash
# From anywhere in the system (if claude-memory-search is in PATH)
claude-memory-search "vue component implementation"

# Or from the semantic-memory-system directory:
cd ~/agents/semantic-memory-system

# Initial setup (first time only)
./setup.sh

# Search for past work
./search.sh "vue component implementation"

# Run health check
python scripts/health_check.py

# Run all tests
./run_tests.sh
```

## Installation

1. Ensure you're in the semantic-memory-system directory
2. Run the setup script:
   ```bash
   ./setup.sh
   ```
   This will:
   - Create virtual environment
   - Install all dependencies
   - Build initial index
   - Run health check

3. Dependencies installed:
   - sentence-transformers
   - chromadb
   - rich
   - spacy
   - pytest

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
python test_system.py
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

- `./setup.sh` - Initial setup and configuration
- `./search.sh <query>` - Quick search interface
- `./reindex.sh` - Rebuild the entire index (with backup)
- `./run_tests.sh` - Run all tests and health checks

### Python Scripts

- `scripts/index_summaries.py` - Index summaries into ChromaDB
- `scripts/memory_search.py` - Semantic search functionality
- `scripts/health_check.py` - System diagnostics and reporting
- `scripts/extract_metadata.py` - Metadata analysis tools

### Testing

Run the test suite with:
```bash
./run_tests.sh
```

Or run specific tests:
```bash
python -m pytest tests/test_metadata_extraction.py -v
python -m pytest tests/test_search_functionality.py -v
```

## Database Location

The vector database is stored at:
```
semantic-memory-system/chroma_db/
```

This persists between sessions, so you only need to index new summaries.

## Extending the System

- **Add more metadata**: Edit `extract_metadata()` in index_summaries.py
- **Adjust scoring**: Modify weights in `search()` method
- **Change embedding model**: Update `EMBEDDING_MODEL` constant
- **Filter by project**: Add project-based filtering to search