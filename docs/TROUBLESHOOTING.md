# Troubleshooting Guide

This guide covers common issues and their solutions for claude-code-vector-memory.

## Installation Issues

### Virtual Environment Problems

**Problem**: `venv/bin/activate` not found or permission denied
```bash
❌ Virtual environment not found!
```

**Solutions**:
1. **Recreate virtual environment**:
   ```bash
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Check Python version**:
   ```bash
   python3 --version  # Should be 3.8+
   which python3
   ```

3. **Fix permissions**:
   ```bash
   chmod +x venv/bin/activate
   chmod +x scripts/*.sh
   ```

### Dependency Installation Failures

**Problem**: `pip install` fails for sentence-transformers or chromadb

**Solutions**:
1. **Update base tools**:
   ```bash
   pip install --upgrade pip setuptools wheel
   ```

2. **Install system dependencies** (Ubuntu/Debian):
   ```bash
   sudo apt update
   sudo apt install python3-dev build-essential
   ```

3. **Install system dependencies** (macOS):
   ```bash
   xcode-select --install
   brew install python@3.9
   ```

4. **Use conda instead of pip**:
   ```bash
   conda create -n claude-memory python=3.9
   conda activate claude-memory
   conda install sentence-transformers chromadb rich spacy pytest
   ```

### ChromaDB Installation Issues

**Problem**: ChromaDB fails to install or import

**Solutions**:
1. **Install with specific version**:
   ```bash
   pip install chromadb==0.4.15
   ```

2. **Clear pip cache**:
   ```bash
   pip cache purge
   pip install --no-cache-dir chromadb
   ```

3. **Use alternative installation**:
   ```bash
   pip install "chromadb[default]"
   ```

## Runtime Issues

### Database Connection Problems

**Problem**: `Collection 'claude_summaries' not found`
```
[red]Collection 'claude_summaries' not found in database.[/red]
```

**Solutions**:
1. **Run initial indexing**:
   ```bash
   python scripts/index_summaries.py
   ```

2. **Check database directory**:
   ```bash
   ls -la chroma_db/
   # Should contain chroma.sqlite3 and UUID directory
   ```

3. **Reset database completely**:
   ```bash
   rm -rf chroma_db/
   python scripts/index_summaries.py
   ```

### Search Returns No Results

**Problem**: Search queries return 0 results or very low similarity scores

**Solutions**:
1. **Lower similarity threshold**:
   ```python
   # In scripts/memory_search.py
   SIMILARITY_THRESHOLD = 0.20  # Lower from 0.30
   ```

2. **Check indexed summaries**:
   ```bash
   python scripts/health_check.py
   ```

3. **Verify summary content**:
   ```bash
   ls ~/.claude/compacted-summaries/
   head -20 ~/.claude/compacted-summaries/summary-*.md
   ```

4. **Rebuild index with verbose output**:
   ```bash
   python scripts/index_summaries.py
   ```

### Embedding Model Issues

**Problem**: `OSError: Can't load tokenizer` or model download fails

**Solutions**:
1. **Clear transformers cache**:
   ```bash
   rm -rf ~/.cache/huggingface/
   ```

2. **Download model manually**:
   ```python
   from sentence_transformers import SentenceTransformer
   model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
   ```

3. **Use offline model**:
   ```bash
   # Download once with internet, then use offline
   python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
   ```

4. **Alternative embedding model**:
   ```python
   # In scripts/index_summaries.py and memory_search.py
   EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Shorter name
   ```

## Performance Issues

### Slow Search Performance

**Problem**: Search takes >5 seconds or times out

**Solutions**:
1. **Check system resources**:
   ```bash
   htop  # Look for high CPU/memory usage
   df -h  # Check disk space
   ```

2. **Optimize ChromaDB**:
   ```bash
   # Rebuild database with optimization
   python reindex.py
   ```

3. **Reduce embedding dimensions** (advanced):
   ```python
   # Use smaller model
   EMBEDDING_MODEL = "all-MiniLM-L12-v2"  # Faster but less accurate
   ```

### Large Database Size

**Problem**: `chroma_db/` directory becomes very large

**Solutions**:
1. **Check database size**:
   ```bash
   du -sh chroma_db/
   ```

2. **Clean up old embeddings**:
   ```bash
   rm -rf chroma_db/
   python scripts/index_summaries.py
   ```

3. **Archive old summaries**:
   ```bash
   mkdir ~/.claude/archived-summaries
   mv ~/.claude/compacted-summaries/summary-2024-*.md ~/.claude/archived-summaries/
   python reindex.py
   ```

## Integration Issues

### Claude Code Commands Not Working

**Problem**: `/system:semantic-memory-search` command not found

**Solutions**:
1. **Check command files exist**:
   ```bash
   ls ~/.claude/commands/system/
   ```

2. **Copy command files manually**:
   ```bash
   mkdir -p ~/.claude/commands/system/
   cp claude-integration/commands/*.md ~/.claude/commands/system/
   ```

3. **Verify CLAUDE.md integration**:
   ```bash
   grep "Memory Integration" ~/.claude/CLAUDE.md
   ```

### Global Search Script Issues

**Problem**: `claude-memory-search` command not found

**Solutions**:
1. **Check PATH**:
   ```bash
   echo $PATH
   which claude-memory-search
   ```

2. **Add to PATH** (add to ~/.bashrc or ~/.zshrc):
   ```bash
   export PATH="$HOME/agents:$PATH"
   ```

3. **Create symlink**:
   ```bash
   ln -sf ~/agents/claude-memory-search ~/.local/bin/claude-memory-search
   ```

4. **Use absolute path**:
   ```bash
   ~/agents/claude-memory-search "search terms"
   ```

## Data Issues

### Missing Summary Files

**Problem**: Health check shows "missing summaries" or "0 indexed summaries"

**Solutions**:
1. **Check summaries directory**:
   ```bash
   ls -la ~/.claude/compacted-summaries/
   ```

2. **Verify file permissions**:
   ```bash
   find ~/.claude/compacted-summaries/ -name "*.md" -type f
   ```

3. **Create test summary** if none exist:
   ```bash
   echo -e "---\ntitle: Test Summary\ndate: $(date +%Y-%m-%d)\n---\n\nThis is a test summary." > ~/.claude/compacted-summaries/test-summary.md
   python scripts/index_summaries.py
   ```

### Corrupted Database

**Problem**: Database errors or inconsistent results

**Solutions**:
1. **Backup and reset**:
   ```bash
   cp -r chroma_db/ chroma_db_backup/
   rm -rf chroma_db/
   python scripts/index_summaries.py
   ```

2. **Check database integrity**:
   ```bash
   python scripts/health_check.py
   ```

3. **Validate with test search**:
   ```bash
   ./search.sh "test query"  # On Linux/macOS
   search.bat "test query"   # On Windows
   ```

## System-Specific Issues

### macOS Issues

**Problem**: Permission denied or code signing issues

**Solutions**:
1. **Allow Python in Security & Privacy**
2. **Use system Python**:
   ```bash
   /usr/bin/python3 -m venv venv
   ```

3. **Install with Homebrew**:
   ```bash
   brew install python@3.9
   /opt/homebrew/bin/python3 -m venv venv
   ```

### Windows Issues (WSL)

**Problem**: Path or permission issues in WSL

**Solutions**:
1. **Use WSL paths consistently**:
   ```bash
   cd /home/username/agents/claude-code-vector-memory
   ```

2. **Fix line endings**:
   ```bash
   dos2unix scripts/*.sh
   chmod +x scripts/*.sh
   ```

3. **Install Windows dependencies**:
   ```bash
   sudo apt install python3-dev gcc g++
   ```

## Diagnostic Commands

Run these to gather information for bug reports:

```bash
# System info
python3 --version
pip --version
uname -a

# Project status
cd ~/agents/claude-code-vector-memory
python scripts/health_check.py
./search.sh "diagnostic test"

# Environment check
which python3
echo $PATH
ls -la venv/bin/

# Database status
ls -la chroma_db/
du -sh chroma_db/

# Dependencies
pip list | grep -E "(chromadb|sentence-transformers|rich)"
```

## Getting Help

If troubleshooting doesn't resolve your issue:

1. **Run full diagnostics** and save output
2. **Check GitHub issues** for similar problems
3. **Create new issue** with:
   - Operating system and version
   - Python version
   - Complete error messages
   - Diagnostic command output
   - Steps to reproduce

Include the output of:
```bash
python ~/agents/claude-code-vector-memory/scripts/health_check.py > health_report.txt
```