#!/usr/bin/env python3
"""Cross-platform setup script for Claude Code Vector Memory System."""
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

def main():
    print("🚀 Claude Code Vector Memory - Setup")
    print("====================================")
    
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
    
    # Determine pip path based on OS
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
    
    print("✅ Dependencies installed")
    
    # Step 3: Download SpaCy model (if needed)
    print("\n🧠 Step 3: Checking SpaCy model...")
    check_spacy = f'"{python_path}" -c "import spacy; spacy.load(\'en_core_web_sm\')"'
    if not run_command(check_spacy, "Checking SpaCy model", check=False):
        print("📥 Downloading SpaCy English model...")
        if not run_command(f'"{python_path}" -m spacy download en_core_web_sm', "Downloading SpaCy model"):
            print("⚠️  SpaCy model download failed, but continuing...")
    else:
        print("✅ SpaCy model already installed")
    
    # Step 4: Initialize ChromaDB
    print("\n🗃️ Step 4: Initializing ChromaDB...")
    chroma_dir = Path("chroma_db")
    if not chroma_dir.exists():
        chroma_dir.mkdir(exist_ok=True)
        print("✅ ChromaDB directory created")
    else:
        print("✅ ChromaDB directory already exists")
    
    # Step 5: Build initial index
    print("\n📚 Step 5: Building initial memory index...")
    index_script = project_dir / "scripts" / "index_summaries.py"
    if not run_command(f'"{python_path}" "{index_script}"', "Building index"):
        print("⚠️  Initial indexing failed, but you can run it later")
    else:
        print("✅ Initial index built")
    
    # Step 6: Run health check
    print("\n🏥 Step 6: Running health check...")
    health_script = project_dir / "scripts" / "health_check.py"
    run_command(f'"{python_path}" "{health_script}"', "Running health check", check=False)
    
    print("\n✅ Setup complete!")
    print("\n📝 Next steps:")
    print("1. Activate virtual environment:")
    if platform.system() == "Windows":
        print("   .\\venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("2. Search your memories:")
    print("   python search.py 'your query'")
    print("\nFor Claude Code integration, see docs/INTEGRATION.md")

if __name__ == "__main__":
    main()