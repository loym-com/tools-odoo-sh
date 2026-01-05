#!/usr/bin/env python3
import sys
import shutil
from pathlib import Path

def main():
    if len(sys.argv) < 3:
        print("Usage: python 1_settings.py <PROJECT_DIR> <PROJECT_VERSION>")
        sys.exit(1)

    project_dir = Path(sys.argv[1])
    project_version = sys.argv[2]

    # Ensure .local exists
    local_dir = project_dir / ".local"
    local_dir.mkdir(parents=True, exist_ok=True)

    # Copy project_settings.py to .local/settings.py
    project_settings = Path(__file__).parent / "project_settings.py"
    settings_dst = local_dir / "settings.py"
    shutil.copy(project_settings, settings_dst)

    # Add PROJECT_VERSION
    with open(settings_dst, "a") as f:
        f.write(f'\nPROJECT_VERSION = "{project_version}"\n')

    print(f"Settings copied to {settings_dst} and PROJECT_VERSION added.")

if __name__ == "__main__":
    main()