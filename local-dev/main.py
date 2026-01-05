#!/usr/bin/env python3
"""
main.py - Run the setup scripts in order
"""

import sys
import subprocess
from pathlib import Path

def run_script(script_name, args=None):
    """Run a Python script with optional arguments"""
    script_dir = Path(__file__).parent
    script_path = script_dir / script_name
    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)
    print(f"Running: {' '.join(cmd)}")
    subprocess.check_call(cmd)

def main():
    if len(sys.argv) < 3:
        print("Usage: python main.py <PROJECT_DIR> <ODOO_VERSION> [key1=value1 key2=value2 ...]")
        sys.exit(1)

    project_dir = Path(sys.argv[1])
    version = sys.argv[2]
    extra_args = sys.argv[3:]

    # 1. Setup settings
    run_script("1_settings.py", [str(project_dir), version])

    # 2. Create odoo.conf and clone repos
    run_script("2_odoo_conf.py", [str(project_dir)] + extra_args)

    # 3. Create venv and install requirements
    run_script("3_venv.py", [str(project_dir)])

    print("Setup complete!")

if __name__ == "__main__":
    main()