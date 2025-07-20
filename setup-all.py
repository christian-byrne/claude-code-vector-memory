#!/usr/bin/env python3
"""Complete setup script with Claude Code integration for all platforms."""
import subprocess
import sys
import os
from pathlib import Path
import platform

def run_command(cmd, description, check=True):
    """Run a command and handle errors."""
    print(f"\n{description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(e.stderr)
        return False

def setup_claude_integration():
    """Set up Claude Code integration."""
    print("\n🔗 Step 5: Setting up Claude Code integration...")
    
    # Create commands directory
    claude_commands = Path.home() / ".claude" / "commands" / "system"
    claude_commands.mkdir(parents=True, exist_ok=True)
    
    # Copy command files
    project_dir = Path(__file__).parent
    commands_src = project_dir / "claude-integration" / "commands"
    
    for cmd_file in commands_src.glob("*.md"):
        dest = claude_commands / cmd_file.name
        dest.write_text(cmd_file.read_text())
        print(f"✅ Copied {cmd_file.name}")
    
    # Handle CLAUDE.md
    claude_md = Path.home() / ".claude" / "CLAUDE.md"
    snippet_file = project_dir / "claude-integration" / "CLAUDE.md-snippet.md"
    
    if claude_md.exists():
        content = claude_md.read_text()
        if "Memory Integration (MANDATORY)" in content:
            print("✅ Memory Integration already configured in CLAUDE.md")
        else:
            print("\n⚠️  Memory Integration not found in CLAUDE.md")
            response = input("Would you like to automatically add it? (y/n): ")
            if response.lower() in ['y', 'yes']:
                # Extract and append the memory integration section
                snippet_content = snippet_file.read_text()
                start = snippet_content.find("## Memory Integration (MANDATORY)")
                end = snippet_content.find("\n\n", start)
                if start != -1:
                    memory_section = snippet_content[start:end] if end != -1 else snippet_content[start:]
                    claude_md.write_text(content + "\n\n" + memory_section)
                    print("✅ Memory Integration added to CLAUDE.md")
            else:
                print("📖 Please manually add the Memory Integration section")
                print("   from claude-integration/CLAUDE.md-snippet.md")
    else:
        print("✅ Creating CLAUDE.md with Memory Integration")
        # Create new CLAUDE.md with just the memory integration
        snippet_content = snippet_file.read_text()
        start = snippet_content.find("## Memory Integration (MANDATORY)")
        if start != -1:
            memory_section = snippet_content[start:]
            claude_md.write_text(memory_section)
    
    # Create global search command (Windows batch file)
    if platform.system() == "Windows":
        agents_dir = Path.home() / "agents"
        agents_dir.mkdir(exist_ok=True)
        
        batch_file = agents_dir / "claude-memory-search.bat"
        batch_content = f"""@echo off
if "%~1"=="" (
    echo Usage: claude-memory-search "search query"
    echo Example: claude-memory-search "vue component implementation"
    exit /b 1
)

cd /d "{project_dir}"
python search.py %*
"""
        batch_file.write_text(batch_content)
        print("✅ Global search command created (claude-memory-search.bat)")
        print("   Add %USERPROFILE%\\agents to your PATH to use globally")
    else:
        # Unix-style global command
        agents_dir = Path.home() / "agents"
        agents_dir.mkdir(exist_ok=True)
        
        script_file = agents_dir / "claude-memory-search"
        script_content = f"""#!/bin/bash
if [ $# -eq 0 ]; then
    echo "Usage: claude-memory-search <search query>"
    exit 1
fi

cd "{project_dir}"
python search.py "$@"
"""
        script_file.write_text(script_content)
        script_file.chmod(0o755)
        print("✅ Global search command created")

def main():
    print("🚀 Claude Code Vector Memory - Complete Setup")
    print("=============================================")
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Step 1: Create virtual environment
    print("\n📦 Step 1: Setting up Python environment...")
    venv_path = Path("venv")
    
    if not venv_path.exists():
        if not run_command(f"{sys.executable} -m venv venv", "Creating virtual environment"):
            return
        print("✅ Virtual environment created")
    else:
        print("✅ Virtual environment already exists")
    
    # Determine paths based on OS
    if platform.system() == "Windows":
        pip_path = venv_path / "Scripts" / "pip"
        python_path = venv_path / "Scripts" / "python"
    else:
        pip_path = venv_path / "bin" / "pip"
        python_path = venv_path / "bin" / "python"
    
    # Step 2: Install dependencies
    print("\n📦 Step 2: Installing dependencies...")
    if not run_command(f'"{pip_path}" install --upgrade pip', "Upgrading pip"):
        return
    
    if not run_command(f'"{pip_path}" install -r requirements.txt', "Installing requirements"):
        return
    
    # Step 3: Download SpaCy model
    print("\n🧠 Step 3: Checking SpaCy model...")
    check_spacy = f'"{python_path}" -c "import spacy; spacy.load(\'en_core_web_sm\')"'
    if not run_command(check_spacy, "Checking SpaCy model", check=False):
        if not run_command(f'"{python_path}" -m spacy download en_core_web_sm', "Downloading SpaCy model"):
            print("⚠️  SpaCy model download failed, continuing anyway...")
    
    # Step 4: Initialize and build index
    print("\n🗃️ Step 4: Building initial memory index...")
    chroma_dir = Path("chroma_db")
    chroma_dir.mkdir(exist_ok=True)
    
    index_script = project_dir / "scripts" / "index_summaries.py"
    if not run_command(f'"{python_path}" "{index_script}"', "Building index"):
        print("⚠️  Initial indexing failed, you can run it later")
    
    # Step 5: Claude Code integration
    setup_claude_integration()
    
    # Step 6: Health check
    print("\n🏥 Step 6: Running health check...")
    health_script = project_dir / "scripts" / "health_check.py"
    run_command(f'"{python_path}" "{health_script}"', "Health check", check=False)
    
    print("\n🎉 Setup complete!")
    print("\n📝 Next steps:")
    if platform.system() == "Windows":
        print("1. Activate virtual environment: .\\venv\\Scripts\\activate")
        print("2. Search: python search.py 'your query'")
        print("3. Global search: claude-memory-search.bat 'your query'")
        print("   (Add %USERPROFILE%\\agents to PATH for 'claude-memory-search')")
    else:
        print("1. Activate virtual environment: source venv/bin/activate")
        print("2. Search: python search.py 'your query'")  
        print("3. Global search: claude-memory-search 'your query'")
    print("4. In Claude Code: /system:semantic-memory-search your query")
    print("\nFor more help, see docs/INTEGRATION.md")

if __name__ == "__main__":
    main()