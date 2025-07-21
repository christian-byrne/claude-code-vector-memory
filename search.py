#!/usr/bin/env python3
"""Cross-platform search script for semantic memory system."""

import subprocess
import sys
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        print("Usage: python search.py <search query>")
        print("Example: python search.py 'vue component implementation'")
        sys.exit(1)

    # Get the search query
    query = " ".join(sys.argv[1:])

    # Find the memory_search.py script
    script_dir = Path(__file__).parent
    memory_search = script_dir / "scripts" / "memory_search.py"

    if not memory_search.exists():
        print(f"Error: {memory_search} not found")
        sys.exit(1)

    # Run the search using the current Python interpreter
    # Note: This script should be called from the shell wrappers that ensure
    # we're using the venv Python, so sys.executable should be correct
    try:
        subprocess.run([sys.executable, str(memory_search), query], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running search: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
