# Semantic Memory System for Claude Code

Give Claude persistent memory across conversations by indexing and searching your session summaries.

## 🚀 Quick Start

### Setup (One Time)

```bash
git clone <this-repo>
cd claude-code-vector-memory

# Run setup
./setup.sh      # Linux/macOS
setup.bat       # Windows
```

The setup automatically:
✅ Creates Python environment  
✅ Installs dependencies  
✅ Sets up Claude Code integration  
✅ Creates global search command  
✅ Configures everything for your OS

### Start Using

```bash
# Search your memories
./search.sh "your query"    # Linux/macOS
search.bat "your query"     # Windows

# From anywhere (after setup)
claude-memory-search "your query"

# In Claude Code
/system:semantic-memory-search your query
```

### Add Your Summaries

1. Place summary files in `claude_summaries/`
2. Run: `python reindex.py`

## Features

- **Semantic Search**: Uses sentence transformers to find conceptually similar past sessions
- **Hybrid Scoring**: Combines semantic similarity (70%), recency (20%), and complexity (10%)
- **Rich Metadata**: Extracts titles, dates, technologies, file paths, and more
- **ChromaDB Backend**: Fast vector similarity search with persistent storage
- **Beautiful CLI**: Rich terminal output with tables and formatted results
- **Cross-Platform**: Works on Linux, macOS, and Windows
- **Claude Code Integration**: Automatic memory search before every task

## How It Works

1. **Index**: Scans your Claude summaries and creates semantic embeddings
2. **Search**: Finds similar past sessions using vector similarity
3. **Integrate**: Claude automatically searches memories before each task
4. **Learn**: Builds on past solutions and approaches

## Project Structure

```
claude-code-vector-memory/
├── setup.sh/setup.bat    # Platform-specific setup scripts
├── search.sh/search.bat  # Platform-specific search scripts
├── reindex.py           # Reindex summaries
├── scripts/             # Core Python scripts
│   ├── index_summaries.py
│   ├── memory_search.py
│   └── health_check.py
└── claude-integration/  # Claude Code integration files
```

## Requirements

- Python 3.8+
- Claude Code
- Your Claude session summaries in `~/.claude/compacted-summaries/`

## Troubleshooting

- **Permission denied?** Run: `chmod +x *.sh` (Linux/macOS)
- **Command not found?** Restart your shell after setup
- **No results?** Make sure you've added summaries and run `python reindex.py`

For more help, see [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

MIT License - see LICENSE file for details.