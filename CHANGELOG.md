# Changelog

All notable changes to claude-code-vector-memory will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of claude-code-vector-memory
- Semantic search for Claude Code session summaries
- ChromaDB vector database integration
- Hybrid scoring (semantic similarity + recency + complexity)
- Rich terminal output with formatted results
- Comprehensive health monitoring and diagnostics
- Unit test suite with pytest
- Shell script interfaces for easy usage
- Claude Code integration with custom commands
- Automatic memory integration via CLAUDE.md
- YAML frontmatter metadata extraction
- Global search script accessible from anywhere

### Features
- **Core System**: Vector-based semantic search using sentence transformers
- **Database**: ChromaDB with persistent storage and 384-dimensional embeddings
- **Search Quality**: Hybrid scoring algorithm balancing relevance and recency
- **Integration**: Seamless Claude Code workflow integration
- **Monitoring**: Health checks and performance metrics
- **Testing**: Comprehensive test coverage for reliability

### Technical Details
- Uses `sentence-transformers/all-MiniLM-L6-v2` embedding model
- Indexes summaries from `~/.claude/compacted-summaries/`
- Similarity threshold of 30% for better recall
- ~130ms average search performance
- Full metadata coverage and extraction

## [1.0.0] - Initial Release

This represents the first stable release ready for public use.