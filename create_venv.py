#!/usr/bin/env python3
import os
import re
import sys
import subprocess

from settings import odoo_core_in_submodules
from settings import github_root

def parse_gitmodules(file_path):
    """Return list of submodule paths from .gitmodules"""
    paths = []
    if not os.path.exists(file_path):
        return paths
    with open(file_path, "r") as f:
        content = f.read()
    matches = re.findall(r'path\s*=\s*(.+)', content)
    for match in matches:
        paths.append(match.strip())
    return paths

def create_and_install_venv(version):
    # Folder of the script
    script_folder = os.path.dirname(os.path.abspath(__file__))

    # Virtual environment folder ../../.venv
    venv_folder = os.path.abspath(os.path.join(script_folder, "../../.venv"))

    # Create virtual environment
    print(f"Creating virtual environment at {venv_folder} ...")
    subprocess.run([sys.executable, "-m", "venv", venv_folder], check=True)

    # Path to pip inside venv
    if os.name == "nt":
        pip_executable = os.path.join(venv_folder, "Scripts", "pip")
    else:
        pip_executable = os.path.join(venv_folder, "bin", "pip")

    # GH folder
    gh_folder = os.path.expanduser(f"{github_root}/{version}/odoo")

    # Paths to install requirements from (main folders)
    if odoo_core_in_submodules:
        main_folders = []
    else:
        main_folders = [
            os.path.join(gh_folder, "odoo"),
            os.path.join(gh_folder, "enterprise"),
            os.path.join(gh_folder, "design-themes"),
            os.path.join(gh_folder, "industry")
        ]

    # Submodules from .gitmodules (next to venv folder)
    gitmodules_file = os.path.join(script_folder, "../..", ".gitmodules")
    submodule_paths = parse_gitmodules(gitmodules_file)
    submodule_abs_paths = [os.path.join(script_folder, "../..", p) for p in submodule_paths]

    all_paths = main_folders + submodule_abs_paths

    # Install requirements.txt if exists
    for folder in all_paths:
        req_file = os.path.join(folder, "requirements.txt")
        if os.path.exists(req_file):
            print(f"Installing {req_file} ...")
            subprocess.run([pip_executable, "install", "-r", req_file], check=True)
        else:
            print(f"No requirements.txt in {folder}, skipping.")

    print("Virtual environment setup complete!")
    print(f"Activate it with:\nsource {os.path.join(venv_folder, 'bin', 'activate')}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python create_venv.py <version>")
        sys.exit(1)
    version = sys.argv[1]
    create_and_install_venv(version)

if __name__ == "__main__":
    main()
