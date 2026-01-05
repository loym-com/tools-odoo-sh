#!/usr/bin/env python3
import os
import re
import sys
from pathlib import Path
import subprocess
import configparser

def parse_repo(url):
    m = re.search(r'(?P<provider>github\.com|gitlab\.com|bitbucket\.org)[:/](?P<user>[^/]+)/(?P<repo>[^/]+)\.git$', url)
    if not m:
        raise ValueError(f"Cannot parse repo URL: {url}")
    return m.group("provider"), m.group("user"), m.group("repo")

def parse_gitmodules(gitmodules_path):
    submodules = []
    if not gitmodules_path.exists():
        return submodules

    config = configparser.ConfigParser()
    config.read(gitmodules_path)

    for section in config.sections():
        if section.startswith('submodule '):
            name_match = re.search(r'submodule "(.*?)"', section)
            if name_match:
                sm = dict(config[section])
                sm['name'] = name_match.group(1)
                submodules.append(sm)
    return submodules

def get_odoo_core_repos(local_dir):
    sys.path.insert(0, str(local_dir))
    from settings import ODOO_CORE_IS_IN_SUBMODULES, ODOO_VERSION, GITHUB_DIR
    if not ODOO_CORE_IS_IN_SUBMODULES:
        return ['odoo', 'design-themes', 'industry', 'enterprise'], ODOO_VERSION, GITHUB_DIR
    return [], None, GITHUB_DIR

def create_venv(project_dir):
    local_dir = project_dir / ".local"
    odoo_repos, version, github_dir = get_odoo_core_repos(local_dir)

    gitmodules_path = project_dir / ".gitmodules"
    submodules = parse_gitmodules(gitmodules_path)

    # Get all paths
    all_paths = []
    for sm in submodules:
        url = sm['url']
        branch = sm['branch']
        try:
            provider, user, repo = parse_repo(url)
            if provider == 'github.com':
                path = github_dir / user / repo / branch
                all_paths.append(str(path))
        except ValueError:
            continue
    for repo in odoo_repos:
        path = github_dir / 'odoo' / repo / version
        all_paths.append(str(path))

    # Create virtual environment
    venv_folder = project_dir / ".venv"
    print(f"Creating virtual environment at {venv_folder} ...")
    subprocess.run([sys.executable, "-m", "venv", str(venv_folder)], check=True)

    # Path to pip inside venv
    if os.name == "nt":
        pip_executable = venv_folder / "Scripts" / "pip"
    else:
        pip_executable = venv_folder / "bin" / "pip"

    # Install requirements.txt if exists
    for folder in all_paths:
        req_file = Path(folder) / "requirements.txt"
        if req_file.exists():
            print(f"Installing {req_file} ...")
            subprocess.run([str(pip_executable), "install", "-r", str(req_file)], check=True)
        else:
            print(f"No requirements.txt in {folder}, skipping.")

    print("Virtual environment setup complete!")
    print(f"Activate it with:\nsource {venv_folder / 'bin' / 'activate'}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python 3_venv.py <PROJECT_DIR>")
        sys.exit(1)

    project_dir = Path(sys.argv[1])
    create_venv(project_dir)

if __name__ == "__main__":
    main()