# Architecture Overview

This document describes the technical architecture of claude-code-vector-memory.

## System Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Query    │───▶│  Memory Search   │───▶│  Search Results │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
           ┌────────────────────┼────────────────────┐
           │                    │                    │
           ▼                    ▼                    ▼
    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
    │   ChromaDB   │    │ Sentence     │    │ Metadata     │
    │  (Vectors)   │    │ Transformer  │    │ Extraction   │
    └──────────────┘    └──────────────┘    └──────────────┘
           ▲                    ▲                    ▲
           │                    │                    │
    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
    │  Indexing    │    │ Embedding    │    │  Summary     │
    │  Process     │    │ Generation   │    │  Files       │
    └──────────────┘    └──────────────┘    └──────────────┘
```

## Core Components

### 1. Vector Database (ChromaDB)
- **Purpose**: Persistent storage of document embeddings and metadata
- **Location**: `~/agents/claude-code-vector-memory/chroma_db/`
- **Collections**: Single collection named "claude_summaries"
- **Dimensions**: 384-dimensional vectors from sentence transformers

### 2. Embedding Model
- **Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Dimensions**: 384
- **Language**: English optimized
- **Performance**: ~213ms for test embedding generation

### 3. Indexing System (`scripts/index_summaries.py`)
- **Source**: `~/.claude/compacted-summaries/*.md`
- **Process**: 
  1. Read markdown files
  2. Extract YAML frontmatter and content
  3. Generate embeddings using sentence transformer
  4. Store in ChromaDB with metadata
- **Metadata Extracted**:
  - Title, date, technologies
  - Complexity level, problem domain
  - File paths, patterns used
  - User preferences, success metrics

### 4. Search System (`scripts/memory_search.py`)
- **Input**: Natural language query
- **Process**:
  1. Convert query to embedding
  2. Find nearest neighbors in vector space
  3. Calculate hybrid scores
  4. Filter by similarity threshold (30%)
  5. Return top 3 results
- **Output**: Formatted results with similarity scores and previews

## Scoring Algorithm

The system uses a hybrid scoring approach:

```python
hybrid_score = (0.7 × semantic_similarity) + 
               (0.2 × recency_score) + 
               (0.1 × complexity_bonus)
```

### Semantic Similarity
- Calculated using L2 distance: `similarity = 1 / (1 + distance)`
- Range: 0.0 to 1.0 (higher is better)
- Threshold: 0.30 minimum for results

### Recency Score
- Linear decay over time: `max(0, 1 - (days_ago / 365))`
- Recent sessions get higher scores
- Prevents old irrelevant results from dominating

### Complexity Bonus
- Based on metadata complexity field
- High complexity sessions get slight boost
- Encourages learning from comprehensive implementations

## Data Flow

### Indexing Flow
1. **Discovery**: Scan `~/.claude/compacted-summaries/` for `.md` files
2. **Parsing**: Extract YAML frontmatter and content
3. **Embedding**: Generate 384-dim vector using sentence transformer
4. **Storage**: Store in ChromaDB with metadata
5. **Validation**: Verify successful indexing

### Search Flow
1. **Query Processing**: Convert user query to embedding
2. **Vector Search**: Find k-nearest neighbors in ChromaDB
3. **Scoring**: Apply hybrid scoring algorithm
4. **Filtering**: Remove results below similarity threshold
5. **Ranking**: Sort by hybrid score (descending)
6. **Presentation**: Format results with Rich library

## Performance Characteristics

### Search Performance
- **Average Query Time**: ~130ms
- **Database Size**: 16.46 MB (9 indexed summaries)
- **Memory Usage**: Embedding model loads ~100MB RAM
- **Scalability**: Linear with number of indexed documents

### Storage Efficiency
- **Embedding Storage**: 384 × 4 bytes = 1.5KB per document
- **Metadata Storage**: Variable, typically 1-2KB per document
- **Content Storage**: Full text stored for preview generation

## File Structure

```
claude-code-vector-memory/
├── scripts/
│   ├── index_summaries.py      # Indexing logic
│   ├── memory_search.py        # Search implementation
│   ├── health_check.py         # System diagnostics
│   └── extract_metadata.py     # Metadata utilities
├── chroma_db/                  # Vector database
│   ├── chroma.sqlite3          # SQLite backend
│   └── [uuid]/                 # Vector storage
├── tests/                      # Unit tests
├── venv/                       # Python virtual environment
└── *.sh                        # Shell script interfaces
```

## Integration Points

### Claude Code Integration
- **Commands**: Custom commands in `~/.claude/commands/system/`
- **Automation**: Mandatory memory search via `CLAUDE.md`
- **Workflow**: Pre-task memory lookup → work → post-task summary

### External Dependencies
- **ChromaDB**: Vector database and similarity search
- **sentence-transformers**: Embedding model and inference
- **Rich**: Terminal output formatting
- **spaCy**: Text processing utilities
- **pytest**: Testing framework

## Security Considerations

### Data Privacy
- **Local Storage**: All data remains on user's machine
- **No Network**: No external API calls during search
- **File Permissions**: Standard user file permissions

### Input Validation
- **Path Sanitization**: Prevent directory traversal
- **Content Filtering**: Handle malformed markdown gracefully
- **Error Handling**: Graceful degradation on corrupted data

## Extensibility

### Adding New Embedding Models
1. Update `EMBEDDING_MODEL` constant
2. Ensure compatible dimensions
3. Rebuild index with new embeddings

### Custom Metadata Fields
1. Extend `extract_metadata()` function
2. Update search filtering logic
3. Modify health check validation

### Alternative Backends
- ChromaDB provides abstraction layer
- Could support other vector databases
- Requires implementing similar collection interface