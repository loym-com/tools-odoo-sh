#!/usr/bin/env python3
import sys
from pathlib import Path
import shutil
import re
import subprocess
import os

from settings_template import ODOO_CORE_IS_IN_SUBMODULES, BASE_DIR

def run(cmd, cwd=None, capture=False):
    if capture:
        return subprocess.check_output(cmd, cwd=cwd, text=True).strip()
    subprocess.check_call(cmd, cwd=cwd)

def parse_gitmodules(gitmodules_path):
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

def parse_repo(url):
    m = re.search(r'[:/](?P<user>[^/]+)/(?P<repo>[^/]+)\.git$', url)
    if not m:
        raise ValueError(f"Cannot parse repo URL: {url}")
    return m.group("user"), m.group("repo")

def clone_repo(url, branch=None):
    user, repo_name = parse_repo(url)
    base = Path.home() / "gh" / user / repo_name
    base.mkdir(parents=True, exist_ok=True)

    default_branch_output = run(["git", "ls-remote", "--symref", url, "HEAD"], capture=True)
    default_branch = None
    for line in default_branch_output.splitlines():
        if line.startswith("ref:"):
            default_branch = line.split()[1].replace("refs/heads/", "")
            break
    if not default_branch:
        raise RuntimeError("Could not determine default branch")

    branch = branch or default_branch

    default_branch_path = base / default_branch
    if not default_branch_path.exists():
        run(["git", "clone", "--branch", default_branch, "--depth", "1", url, str(default_branch_path)])

    git_symlink = base / ".git"
    if not git_symlink.exists():
        git_symlink.symlink_to(default_branch_path / ".git", target_is_directory=True)

    if branch != default_branch:
        worktree_path = base / branch
        if not worktree_path.exists():
            run(["git", "worktree", "add", str(worktree_path), branch], cwd=default_branch_path)
        return worktree_path
    else:
        return default_branch_path

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <version>")
        sys.exit(1)

    version = sys.argv[1]
    PROJECT_DIR = Path.cwd()
    local_folder = PROJECT_DIR / ".local"
    local_folder.mkdir(exist_ok=True)

    # Copy settings_template.py to .local/settings.py
    settings_src = PROJECT_DIR / "settings_template.py"
    settings_dst = local_folder / "settings.py"
    shutil.copy(settings_src, settings_dst)

    # Add PROJECT_VERSION = version
    with open(settings_dst, "a") as f:
        f.write(f'\nPROJECT_VERSION = "{version}"\n')

    # Parse .gitmodules
    gitmodules_path = PROJECT_DIR / ".gitmodules"
    submodules = parse_gitmodules(gitmodules_path)

    # Clone submodules
    for sm in submodules:
        url = sm['url']
        branch = sm.get('branch', None)
        clone_repo(url, branch)

    # Clone odoo core if not in submodules
    if not ODOO_CORE_IS_IN_SUBMODULES:
        odoo_repos = [
            ("https://github.com/odoo/odoo.git", "odoo"),
            ("https://github.com/odoo/enterprise.git", "enterprise"),
            ("https://github.com/odoo/design-themes.git", "design-themes"),
            ("https://github.com/odoo/industry.git", "industry"),
        ]
        for url, name in odoo_repos:
            clone_repo(url, version)

    # Create .venv
    venv_folder = PROJECT_DIR / ".venv"
    run([sys.executable, "-m", "venv", str(venv_folder)])
    pip = venv_folder / "bin" / "pip"

    # Paths to check for requirements
    paths_to_check = []
    for sm in submodules:
        user, repo = parse_repo(sm['url'])
        branch = sm.get('branch', 'main')
        path = Path.home() / "gh" / user / repo / branch
        paths_to_check.append(path)

    if not ODOO_CORE_IS_IN_SUBMODULES:
        for _, name in odoo_repos:
            path = Path.home() / "gh" / "odoo" / name / version
            paths_to_check.append(path)

    for path in paths_to_check:
        req = path / "requirements.txt"
        if req.exists():
            run([str(pip), "install", "-r", str(req)])

    # Create symlinks in .local
    for sm in submodules:
        user, repo = parse_repo(sm['url'])
        branch = sm.get('branch', 'main')
        target = Path.home() / "gh" / user / repo / branch
        link_path = local_folder / sm['path']
        link_path.parent.mkdir(parents=True, exist_ok=True)
        if not link_path.exists():
            os.symlink(target, link_path)

    if not ODOO_CORE_IS_IN_SUBMODULES:
        for _, name in odoo_repos:
            target = Path.home() / "gh" / "odoo" / name / version
            link_path = local_folder / name
            if not link_path.exists():
                os.symlink(target, link_path)

    # Create odoo.conf
    conf_file = local_folder / "odoo.conf"
    with open(conf_file, "w") as f:
        f.write("[options]\n")
        f.write("addons_path = .local\n")
        defaults = {
            "admin_passwd": "admin",
            "dbfilter": ".*",
            "db_host": "localhost",
            "db_name": PROJECT_DIR.name,
            "db_port": "5432",
            "db_user": "odoo",
            "db_password": "odoo",
            "http_interface": "127.0.0.1",
            "http_port": "8069",
            "log_level": "info",
            "xmlrpc_port": "8069"
        }
        for key in sorted(defaults):
            f.write(f"{key} = {defaults[key]}\n")

    print("Setup complete")

if __name__ == "__main__":
    main()