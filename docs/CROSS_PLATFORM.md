# Cross-Platform Compatibility Guide

## Overview

The Claude Code Vector Memory system is designed to work on all major operating systems. However, there are some differences in how you run the scripts.

## Platform Support

| Feature | Linux | macOS | Windows | Windows (WSL) |
|---------|-------|-------|---------|---------------|
| Shell scripts (.sh) | ✅ | ✅ | ❌ | ✅ |
| Python scripts (.py) | ✅ | ✅ | ✅ | ✅ |
| Virtual environments | ✅ | ✅ | ✅ | ✅ |
| Claude Code integration | ✅ | ✅ | ✅* | ✅ |

*Windows users need to use Python scripts or WSL for full functionality

## Running Scripts by Platform

### Linux/macOS

Use the shell scripts directly:
```bash
./scripts/setup-all.sh
./scripts/search.sh "query"
./scripts/reindex.sh
```

### Windows (Native)

Use the Python equivalents:
```bash
python setup.py
python search.py "query"
python scripts/index_summaries.py  # Instead of reindex.sh
```

### Windows (with WSL or Git Bash)

You can use the shell scripts:
```bash
./scripts/setup-all.sh
./scripts/search.sh "query"
```

## Path Considerations

### Home Directory
- Linux/macOS: `~/` works everywhere
- Windows: Use `%USERPROFILE%` in Command Prompt or `$HOME` in PowerShell

### Virtual Environment Activation
- Linux/macOS: `source venv/bin/activate`
- Windows: `.\venv\Scripts\activate`

## Known Limitations

1. **Shell Scripts on Windows**: The `.sh` scripts require WSL, Git Bash, or similar Unix-like environment
2. **File Permissions**: `chmod +x` doesn't work on Windows (not needed for Python scripts)
3. **Global Commands**: The `claude-memory-search` global command requires manual PATH setup on Windows

## Recommendations

### For Windows Users

1. **Option 1**: Use Windows Subsystem for Linux (WSL2) for the best experience
2. **Option 2**: Use the Python scripts (`setup.py`, `search.py`) instead of shell scripts
3. **Option 3**: Install Git for Windows which includes Git Bash

### For All Users

- Python scripts work identically across all platforms
- Always use forward slashes in paths within Python code
- Use `pathlib` for path manipulation (already done in this project)

## Testing Cross-Platform Compatibility

Run these commands to verify your setup works:

```bash
# Check Python
python --version

# Check pip
python -m pip --version

# Test the search (after setup)
python search.py "test query"
```

If you encounter platform-specific issues, please check `docs/TROUBLESHOOTING.md` or report them as GitHub issues.