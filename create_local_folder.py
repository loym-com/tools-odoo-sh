#!/usr/bin/env python3
import os
from pathlib import Path
import re

# Base directory for local repos
BASE_DIR = Path.home() / "gh"
# Name of the local helper folder inside the repo
PROJECT_RC_DIR = ".local"  # hidden, ignored by Git

def parse_gitmodules(gitmodules_path):
    """Parse .gitmodules and return a list of submodule dicts with keys: name, path, url, branch"""
    submodules = []
    if not gitmodules_path.exists():
        return submodules

    current = {}
    with open(gitmodules_path, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("[submodule"):
                if current:
                    submodules.append(current)
                    current = {}
                match = re.match(r'\[submodule "(.*?)"\]', line)
                if match:
                    current['name'] = match.group(1)
            elif "=" in line:
                key, value = map(str.strip, line.split("=", 1))
                current[key] = value
        if current:
            submodules.append(current)
    return submodules

def get_local_submodule_path(submodule):
    """Compute ~/gh/ORG/REPO/BRANCH path from submodule"""
    url = submodule.get("url")
    branch = submodule.get("branch", "main")
    match = re.match(r'(?:git@github\.com:|https://github\.com/)([^/]+)/([^.]+)(?:\.git)?', url)
    if not match:
        raise ValueError(f"Cannot parse URL: {url}")
    org, repo = match.groups()
    return BASE_DIR / org / repo / branch

def setup_local_folder():
    """Create ignored local folder with odoo.conf and symlinks"""
    repo_root = Path(".").resolve()
    local_folder = repo_root / PROJECT_RC_DIR
    local_folder.mkdir(exist_ok=True)
    print(f"Created local helper folder: {local_folder}")

    # Create a minimal odoo.conf
    odoo_conf_path = local_folder / "odoo.conf"
    if not odoo_conf_path.exists():
        odoo_conf_path.write_text("[options]\naddons_path = .\n")
        print(f"Created {odoo_conf_path}")

    # Parse submodules and create symlinks
    gitmodules_path = repo_root / ".gitmodules"
    submodules = parse_gitmodules(gitmodules_path)

    for sm in submodules:
        try:
            target_path = get_local_submodule_path(sm)
            link_path = local_folder / sm['path'] / sm.get("branch", "main")
            link_path.parent.mkdir(parents=True, exist_ok=True)
            if not link_path.exists():
                os.symlink(target_path, link_path)
                print(f"Created symlink: {link_path} -> {target_path}")
        except Exception as e:
            print(f"Error creating symlink for {sm.get('name')}: {e}")

    # Suggest adding to .gitignore
    gitignore_path = repo_root / ".gitignore"
    ignore_line = f"/{PROJECT_RC_DIR}"
    if gitignore_path.exists():
        with open(gitignore_path) as f:
            lines = f.read().splitlines()
        if ignore_line not in lines:
            with open(gitignore_path, "a") as f:
                f.write(f"\n{ignore_line}\n")
            print(f"Added {PROJECT_RC_DIR} to .gitignore")
    else:
        gitignore_path.write_text(f"{PROJECT_RC_DIR}\n")
        print(f"Created .gitignore and added {PROJECT_RC_DIR}")

if __name__ == "__main__":
    setup_local_folder()
