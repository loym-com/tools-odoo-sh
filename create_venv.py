#!/usr/bin/env python3
import os
import re
import sys
import subprocess

from settings import odoo_core_in_submodules
from settings import github_root
from settings import project_root as default_project_root

print(odoo_core_in_submodules)

def run(cmd, cwd=None, capture=False):
    """Run a shell command"""
    if capture:
        return subprocess.check_output(cmd, cwd=cwd, text=True).strip()
    subprocess.check_call(cmd, cwd=cwd)

def parse_gitmodules(file_path):
    """
    Parse .gitmodules and return a list of tuples:
        [(submodule_path, submodule_url), ...]
    """
    submodules = []
    if not os.path.exists(file_path):
        return submodules

    content = Path(file_path).read_text()
    # Matches lines like: path = submoduleX
    path_matches = re.findall(r'path\s*=\s*(.+)', content)
    # Matches lines like: url = git@github.com:USER/submoduleX.git
    url_matches = re.findall(r'url\s*=\s*(.+)', content)

    for path, url in zip(path_matches, url_matches):
        submodules.append((path.strip(), url.strip()))
    return submodules

# def parse_gitmodules(file_path):
#     """Return list of submodule paths from .gitmodules"""
#     paths = []
#     if not os.path.exists(file_path):
#         return paths
#     with open(file_path, "r") as f:
#         content = f.read()
#     matches = re.findall(r'path\s*=\s*(.+)', content)
#     for match in matches:
#         paths.append(match.strip())
#     return paths

def ensure_submodule_worktree(project_root, path, url):
    """
    Ensure the submodule exists as a git worktree.
    project_root: Path to main repo
    path: relative path of submodule inside main repo
    url: remote URL of submodule
    """
    submodule_root = project_root / path
    submodule_root.mkdir(parents=True, exist_ok=True)

    # If already a git repo, do nothing
    if (submodule_root / ".git").exists():
        print(f"Submodule {path} exists at {submodule_root}")
        return submodule_root

    # Clone shallow to target location
    print(f"Cloning submodule {path} from {url} into {submodule_root}")
    run(["git", "clone", "--depth", "1", url, str(submodule_root)])

    # Optional: make a worktree branch for local development
    # Here we can create a branch matching the default branch
    os.chdir(submodule_root)
    default_branch = run(
        ["git", "ls-remote", "--symref", "origin", "HEAD"], capture=True
    ).splitlines()[0].split()[-1].replace("refs/heads/", "")
    run(["git", "checkout", default_branch])

    return submodule_root

def create_and_install_venv(project_root=None):
    """
    Create and install virtualenv.

    Parameters:
        project_root: str or Path (optional)
            If None, uses settings.project_root.
            Always converted to Path internally.
    """
    if project_root is None:
        project_root = default_project_root

    # Convert to Path if not already
    project_root = Path(project_root)

    # Virtual environment folder ../../.venv
    venv_folder = f"{project_root}/.venv"

    # Create virtual environment
    print(f"Creating virtual environment at {venv_folder} ...")
    subprocess.run([sys.executable, "-m", "venv", venv_folder], check=True)

    # Path to pip inside venv
    if os.name == "nt":
        pip_executable = os.path.join(venv_folder, "Scripts", "pip")
    else:
        pip_executable = os.path.join(venv_folder, "bin", "pip")

    # GH folder
    gh_folder = os.path.expanduser(f"{github_root}/odoo")

    # Paths to install requirements from (main folders)
    if odoo_core_in_submodules:
        main_folders = []
    else:
        main_folders = [
            os.path.join(gh_folder, "odoo/odoo"),
            os.path.join(gh_folder, "enterprise"),
            os.path.join(gh_folder, "design-themes"),
            os.path.join(gh_folder, "industry")
        ]

    # Submodules from .gitmodules (next to venv folder)
    submodule_paths = parse_gitmodules(f"{project_root}/.gitmodules")
    submodule_abs_paths = [os.path.join(project_root, p) for p in submodule_paths]

    all_paths = main_folders + submodule_abs_paths
    print(all_paths)

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
    import argparse

    parser = argparse.ArgumentParser(description="Create and install a virtual environment")
    parser.add_argument(
        "project_root",
        nargs="?",
        default=None,
        help="Path to the project root (defaults to settings.project_root)",
    )
    args = parser.parse_args()

    create_and_install_venv(args.project_root)

if __name__ == "__main__":
    main()
