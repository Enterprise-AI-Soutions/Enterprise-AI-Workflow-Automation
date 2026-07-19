#!/usr/bin/env python3
"""
setup.py — One-shot local setup script.

Usage:
    python scripts/setup.py
"""

import subprocess
import sys
import os
from pathlib import Path

ROOT = Path(__file__).parent.parent


def run(cmd: str, **kwargs):
    print(f"\n🔧 {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=ROOT, **kwargs)
    if result.returncode != 0:
        print(f"❌ Command failed: {cmd}")
        sys.exit(1)


def main():
    print("🚀 Enterprise AI Workflow Automation — Setup\n")

    # Check Python version
    if sys.version_info < (3, 11):
        print("❌ Python 3.11+ is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")

    # Create venv if needed
    venv_path = ROOT / "venv"
    if not venv_path.exists():
        run(f"{sys.executable} -m venv venv")
        print("✅ Virtual environment created")

    # Activate path for pip
    if sys.platform == "win32":
        pip = str(venv_path / "Scripts" / "pip")
    else:
        pip = str(venv_path / "bin" / "pip")

    run(f"{pip} install --upgrade pip")
    run(f"{pip} install -r requirements.txt")

    # Dev deps
    dev_req = ROOT / "requirements-dev.txt"
    if dev_req.exists():
        run(f"{pip} install -r requirements-dev.txt")

    # Copy .env if missing
    env_file = ROOT / ".env"
    env_example = ROOT / ".env.example"
    if not env_file.exists() and env_example.exists():
        import shutil
        shutil.copy(env_example, env_file)
        print("✅ .env created from .env.example — please edit it with your API keys")
    elif env_file.exists():
        print("✅ .env already exists")

    # Create logs dir
    logs_dir = ROOT / "logs"
    logs_dir.mkdir(exist_ok=True)

    print("\n✨ Setup complete!")
    print("\nNext steps:")
    print("  1. Edit .env with your API keys")
    print("  2. Activate venv:")
    if sys.platform == "win32":
        print("       venv\\Scripts\\activate")
    else:
        print("       source venv/bin/activate")
    print("  3. Run the server:")
    print("       uvicorn app.main:app --reload")
    print("  4. Open http://localhost:8000")
    print("\nOr run with Docker:")
    print("  docker-compose up --build")


if __name__ == "__main__":
    main()
