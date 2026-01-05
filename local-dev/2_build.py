#!/usr/bin/env python3
import os
import re
import sys
from pathlib import Path
import subprocess

from gitclone import main as gitclone_main
from utils import get_settings, get_submodules, get_repos

def clone_repos(project_dir, repos):
    search_dir = project_dir / ".local" / "search"
    search_dir.mkdir(parents=True, exist_ok=True)
    for repo in repos:
        url = repo['url']
        branch = repo['branch']
        sys.argv = ["gitclone.py", url, "-b", branch]
        gitclone_main()

        search_dir = Path(repo['search_dir'])
        repo_dir = Path(repo['repo_dir'])
        if not search_dir.exists():
            print(f"Creating symbolic link: {search_dir} -> {repo_dir}")
            search_dir.symlink_to(repo_dir, target_is_directory=True)
        else:
            pass # print(f"Symbolic link already exists: {search_dir}")

def create_odoo_conf(project_dir, repos, extra_params):
    settings = get_settings(project_dir)

    # Calculate default port based on Odoo version
    major_version = int(settings.ODOO_VERSION.split('.')[0])
    default_port = str(major_version * 1000)

    # Default configurations
    defaults = {
        "admin_passwd": "admin",
        "auth_admin_passkey_password": "admin",
        "dbfilter": ".*",
        "db_host": "localhost",
        "db_name": "",
        "db_port": "5432",
        "db_user": "odoo",
        "db_password": "odoo",
        "http_interface": "127.0.0.1",
        "http_port": default_port,
        "log_level": "info",
    }

    # Override defaults with user-provided key=value
    for kv in extra_params:
        if '=' in kv:
            key, value = kv.split('=', 1)
            defaults[key] = value

    # addons_path
    addons_path = []
    for repo in repos:
        repo_dir = Path(repo["repo_dir"])
        if str(repo_dir).endswith(f"odoo/{settings.ODOO_VERSION}"):
            addons_path.append(repo_dir / "addons")
        else:
            addons_path.append(repo_dir)
    addons_path_str = ",\n              ".join(map(str, addons_path))

    # Write odoo.conf
    local_folder = project_dir / ".local"
    local_folder.mkdir(exist_ok=True)
    conf_file = local_folder / "odoo.conf"
    with open(conf_file, "w") as f:
        f.write("[options]\n")
        # Write configurations sorted alphabetically (except addons_path)
        for key in sorted(defaults):
            f.write(f"{key} = {defaults[key]}\n")
        # Addons_path always last
        f.write(f"addons_path = {addons_path_str}\n")

    print(f"odoo.conf created at {conf_file}")
    print("Configurations (alphabetically):")
    for key in sorted(defaults):
        print(f"{key} = {defaults[key]}")
    print("addons_path:")
    print(addons_path_str)

def create_venv(project_dir, repos):
    settings = get_settings(project_dir)

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
    for repo in repos:
        repo_dir = repo['repo_dir']
        req_file = Path(repo_dir) / "requirements.txt"
        if req_file.exists():
            print(f"Installing {req_file} ...")
            subprocess.run([str(pip_executable), "install", "-r", str(req_file)], check=True)
        else:
            print(f"No requirements.txt in {repo_dir}, skipping.")

    # Provide next steps for the user
    print("Virtual environment setup complete! Next steps:")
    print("")
    print("source .venv/bin/activate")
    print(f"python3 {settings.GITHUB_DIR}/odoo/odoo/{settings.ODOO_VERSION}/odoo-bin -c ./.local/odoo.conf")
    print("")

def main():
    if len(sys.argv) < 2:
        print("Usage: python 2_odoo_conf.py <PROJECT_DIR> [key=value ...]")
        sys.exit(1)

    project_dir = Path(sys.argv[1]).resolve()
    extra_params = sys.argv[2:]

    # Repos
    submodules = get_submodules(project_dir)
    repos = get_repos(project_dir, submodules)

    # Call functions
    print("begin clone repos and create symlinks...")
    clone_repos(project_dir, repos) # and create search_dir symlinks

    print("begin create odoo.conf...")
    create_odoo_conf(project_dir, repos, extra_params)

    print("begin create virtual environment...")
    create_venv(project_dir, repos)

if __name__ == "__main__":
    main()