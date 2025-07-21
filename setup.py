#!/usr/bin/env python3
"""
Complete setup script for Claude Code Vector Memory System.
Handles all platforms and Claude Code integration.
"""

import os
import platform
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description, check=True):
    """Run a command and handle errors."""
    print(f"\n{description}...")
    try:
        result = subprocess.run(
            cmd, shell=True, check=check, capture_output=True, text=True
        )
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(e.stderr)
        return False


def setup_python_environment():
    """Install Python dependencies."""
    print("\n📦 Installing Python dependencies...")

    # We're already in the venv (activated by setup.sh/setup.bat)
    # Upgrade pip first
    if not run_command("pip install --upgrade pip", "Upgrading pip"):
        return False

    # Install requirements
    if not run_command("pip install -r requirements.txt", "Installing requirements"):
        return False

    print("✅ Dependencies installed")

    # Try to install SpaCy model if needed
    print("\n🧠 Checking SpaCy model...")
    check_spacy = "python -c \"import spacy; spacy.load('en_core_web_sm')\""
    if not run_command(check_spacy, "Checking SpaCy model", check=False):
        print("📥 Downloading SpaCy English model...")
        if not run_command(
            "python -m spacy download en_core_web_sm",
            "Downloading SpaCy model",
            check=False,
        ):
            print("⚠️  SpaCy model download failed, but continuing...")
    else:
        print("✅ SpaCy model already installed")

    return True


def build_initial_index():
    """Build the initial ChromaDB index."""
    print("\n🗃️ Building initial memory index...")

    # Create ChromaDB directory
    chroma_dir = Path("chroma_db")
    chroma_dir.mkdir(exist_ok=True)

    # Run indexing script
    index_script = Path("scripts") / "index_summaries.py"
    if not run_command(f"python {index_script}", "Building index", check=False):
        print(
            "⚠️  Initial indexing failed - you can run it later after adding summaries"
        )
    else:
        print("✅ Initial index built")

    return True


def setup_claude_integration():
    """Set up Claude Code integration with OS-specific paths."""
    print("\n🔗 Setting up Claude Code integration...")

    project_dir = Path.cwd()
    is_windows = platform.system() == "Windows"

    # Determine the search script extension
    search_script = "search.bat" if is_windows else "search.sh"

    # Create commands directory
    claude_commands = Path.home() / ".claude" / "commands" / "system"
    claude_commands.mkdir(parents=True, exist_ok=True)

    # Read command templates
    commands_src = project_dir / "claude-integration" / "commands"

    for cmd_file in commands_src.glob("*.md"):
        # Read the content
        content = cmd_file.read_text()

        # Replace the search script path based on OS
        content = content.replace(
            "~/agents/claude-code-vector-memory/scripts/search.sh",
            f"~/agents/claude-code-vector-memory/{search_script}",
        )

        # Write to destination
        dest = claude_commands / cmd_file.name
        if dest.exists():
            # Check if content is different
            existing_content = dest.read_text()
            if existing_content != content:
                print(f"⚠️  {cmd_file.name} already exists with different content")
                response = input("   Overwrite? (y/n): ")
                if response.lower() in ["y", "yes"]:
                    dest.write_text(content)
                    print(f"✅ Updated {cmd_file.name}")
                else:
                    print(f"⏭️  Skipped {cmd_file.name}")
            else:
                print(f"✅ {cmd_file.name} already up to date")
        else:
            dest.write_text(content)
            print(f"✅ Installed {cmd_file.name}")

    # Handle CLAUDE.md
    claude_md = Path.home() / ".claude" / "CLAUDE.md"
    snippet_file = project_dir / "claude-integration" / "CLAUDE.md-snippet.md"

    # Read snippet and update paths
    snippet_content = snippet_file.read_text()
    snippet_content = snippet_content.replace(
        "~/agents/claude-code-vector-memory/scripts/search.sh",
        f"~/agents/claude-code-vector-memory/{search_script}",
    )

    if claude_md.exists():
        content = claude_md.read_text()
        if "Memory Integration (MANDATORY)" in content:
            print("✅ Memory Integration already configured in CLAUDE.md")
        else:
            print("\n⚠️  Memory Integration not found in CLAUDE.md")
            response = input("Would you like to add it automatically? (y/n): ")
            if response.lower() in ["y", "yes"]:
                # Extract memory integration section
                start = snippet_content.find("## Memory Integration (MANDATORY)")
                if start != -1:
                    # Find the end of the section (next ## or end of file)
                    end = snippet_content.find("\n##", start + 1)
                    memory_section = (
                        snippet_content[start:end]
                        if end != -1
                        else snippet_content[start:]
                    )

                    # Append to CLAUDE.md
                    with open(claude_md, "a") as f:
                        f.write("\n\n" + memory_section)
                    print("✅ Memory Integration added to CLAUDE.md")
            else:
                print("📖 Please manually add the Memory Integration section")
                print(f"   from {snippet_file}")
    else:
        print("📝 Creating CLAUDE.md with Memory Integration...")
        # Extract just the memory integration section
        start = snippet_content.find("## Memory Integration (MANDATORY)")
        if start != -1:
            end = snippet_content.find("\n##", start + 1)
            memory_section = (
                snippet_content[start:end] if end != -1 else snippet_content[start:]
            )
            claude_md.write_text(memory_section)
            print("✅ Created CLAUDE.md with Memory Integration")

    # Create global search command
    create_global_search_command(project_dir, is_windows)

    return True


def create_global_search_command(project_dir, is_windows):
    """Create a global search command for the system."""
    agents_dir = Path.home() / "agents"
    agents_dir.mkdir(exist_ok=True)

    if is_windows:
        # Create batch file for Windows
        batch_file = agents_dir / "claude-memory-search.bat"
        batch_content = f"""@echo off
if "%~1"=="" (
    echo Usage: claude-memory-search "search query"
    echo Example: claude-memory-search "vue component implementation"
    exit /b 1
)

cd /d "{project_dir}"
call search.bat %*
"""
        batch_file.write_text(batch_content)
        print("✅ Global search command created (claude-memory-search.bat)")
        print("   Add %USERPROFILE%\\agents to your PATH to use it globally")
    else:
        # Create shell script for Unix
        script_file = agents_dir / "claude-memory-search"
        script_content = f"""#!/bin/bash
if [ $# -eq 0 ]; then
    echo "Usage: claude-memory-search <search query>"
    echo "Example: claude-memory-search 'vue component implementation'"
    exit 1
fi

cd "{project_dir}"
./search.sh "$@"
"""
        script_file.write_text(script_content)
        script_file.chmod(0o755)
        print("✅ Global search command created (claude-memory-search)")

        # Add to PATH if not already there
        if str(agents_dir) not in os.environ.get("PATH", ""):
            shell_config = Path.home() / (
                ".zshrc" if os.path.exists(Path.home() / ".zshrc") else ".bashrc"
            )

            # Check if already in shell config
            if shell_config.exists():
                config_content = shell_config.read_text()
                if "$HOME/agents" not in config_content:
                    with open(shell_config, "a") as f:
                        f.write(
                            "\n# Add agents directory to PATH for claude-memory-search\n"
                        )
                        f.write('export PATH="$HOME/agents:$PATH"\n')
                    print(f"✅ Added ~/agents to PATH in {shell_config.name}")
                    print("   Restart your shell or run: source ~/" + shell_config.name)


def run_health_check():
    """Run system health check."""
    print("\n🏥 Running system health check...")
    health_script = Path("scripts") / "health_check.py"
    run_command(f"python {health_script}", "Health check", check=False)


def main():
    """Main setup function."""
    print("🚀 Claude Code Vector Memory - Complete Setup")
    print("=============================================")

    # Check that we're in the right directory
    if not Path("requirements.txt").exists():
        print("❌ Error: requirements.txt not found")
        print("   Please run this script from the claude-code-vector-memory directory")
        sys.exit(1)

    # Step 1: Python environment (dependencies)
    if not setup_python_environment():
        print("\n❌ Setup failed during dependency installation")
        sys.exit(1)

    # Step 2: Build initial index
    build_initial_index()

    # Step 3: Claude Code integration
    setup_claude_integration()

    # Step 4: Health check
    run_health_check()

    # Success!
    print("\n🎉 Setup complete!")
    print("\n📝 Next steps:")
    print("1. Place your Claude summaries in claude_summaries/")
    print("2. Run: python reindex.py")
    print("3. Search: ./search.sh 'your query' (or search.bat on Windows)")
    print("4. In Claude Code: /system:semantic-memory-search your query")
    print("\nFor more information, see README.md")


if __name__ == "__main__":
    main()
