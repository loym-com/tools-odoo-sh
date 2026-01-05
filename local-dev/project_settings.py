# settings.py

from pathlib import Path

ENTERPRISE = True

BASE_DIR = Path.home() / "src"

GITHUB_DIR = BASE_DIR / "gh"

PROJECT_DIR = Path(__file__).resolve().parents[1]
