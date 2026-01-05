#!/usr/bin/env python3
import os
import re
import sys
from pathlib import Path
import subprocess

import configparser

def parse_gitmodules(gitmodules_path):
    submodules = []
    if not gitmodules_path.exists():
        return submodules

    config = configparser.ConfigParser()
    config.read(gitmodules_path)

    for section in config.sections():
        if section.startswith('submodule '):
            # Extract name from [submodule "name"]
            name_match = re.search(r'submodule "(.*?)"', section)
            if name_match:
                sm = dict(config[section])
                sm['name'] = name_match.group(1)
                submodules.append(sm)
    return submodules

def parse_repo(url):
    m = re.search(r'(?P<provider>github\.com|gitlab\.com|bitbucket\.org)[:/](?P<user>[^/]+)/(?P<repo>[^/]+)\.git$', url)
    if not m:
        raise ValueError(f"Cannot parse repo URL: {url}")
    return m.group("provider"), m.group("user"), m.group("repo")

def get_odoo_core_repos(local_dir):
    sys.path.insert(0, str(local_dir))
    from settings import ODOO_CORE_IS_IN_SUBMODULES, ODOO_VERSION
    if not ODOO_CORE_IS_IN_SUBMODULES:
        return ['odoo', 'design-themes', 'industry', 'enterprise'], ODOO_VERSION
    return [], None

def create_odoo_conf(project_dir, extra_params, submodules):
    # Import settings from .local
    local_dir = project_dir / ".local"
    odoo_repos, version = get_odoo_core_repos(local_dir)
    
    sys.path.insert(0, str(local_dir))
    try:
        from settings import GITHUB_DIR, ODOO_VERSION
    except ImportError:
        print("Could not import GITHUB_DIR from .local/settings.py")
        sys.exit(1)

    # Calculate default port based on Odoo version
    major_version = int(ODOO_VERSION.split('.')[0])
    default_port = str(major_version * 1000)

    # Default configurations
    defaults = {
        "admin_passwd": "admin",
        "auth_admin_passkey_password": "admin",
        "dbfilter": ".*",
        "db_host": "localhost",
        "db_name": project_dir.name,
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

    # Build repos from submodules and odoo_repos
    repos = []
    for sm in submodules:
        url = sm['url']
        branch = sm['branch']
        try:
            provider, user, repo = parse_repo(url)
            repos.append((provider, user, repo, branch))
        except ValueError:
            continue
    for repo in odoo_repos:
        repos.append(('github.com', 'odoo', repo, version))

    # Get all addons paths
    all_addons = []
    for provider, user, repo, branch in repos:
        if provider == 'github.com':
            path = GITHUB_DIR / user / repo / branch
            if repo == 'odoo':
                path = path / "addons"
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        all_addons.append(str(path))

    # Format addons_path with line breaks and indentation
    addons_path_str = ",\n              ".join(all_addons)

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

def main():
    if len(sys.argv) < 2:
        print("Usage: python 2_odoo_conf.py <PROJECT_DIR> [key=value ...]")
        sys.exit(1)

    project_dir = Path(sys.argv[1])
    extra_params = sys.argv[2:]

    local_dir = project_dir / ".local"
    sys.path.insert(0, str(local_dir))
    try:
        from settings import ODOO_CORE_IS_IN_SUBMODULES, GITHUB_DIR, ODOO_VERSION
    except ImportError:
        print("Could not import required settings from .local/settings.py")
        sys.exit(1)

    gitmodules_path = project_dir / ".gitmodules"
    submodules = parse_gitmodules(gitmodules_path)

    # Sort submodules by path
    submodules.sort(key=lambda sm: sm['path'])

    odoo_repos, odoo_version = get_odoo_core_repos(local_dir)

    # Clone missing repos from submodules
    script_dir = Path(__file__).parent
    gitclone_script = script_dir / "gitclone.py"
    for sm in submodules:
        url = sm['url']
        branch = sm['branch']
        try:
            provider, user, repo = parse_repo(url)
            if provider == 'github.com':
                path = GITHUB_DIR / user / repo / branch
                if not path.exists():
                    print(f"Cloning {user}/{repo} branch {branch}...")
                    cmd = [sys.executable, str(gitclone_script), f'git@{provider}:{user}/{repo}.git', '-b', branch]
                    subprocess.check_call(cmd)
            else:
                print(f"Skipping {provider}/{user}/{repo}, unsupported provider")
        except ValueError as e:
            print(e)
            continue

    # Clone odoo repos
    for repo in odoo_repos:
        branch = odoo_version
        path = GITHUB_DIR / 'odoo' / repo / branch
        if not path.exists():
            print(f"Cloning odoo/{repo} branch {branch}...")
            cmd = [sys.executable, str(gitclone_script), f'git@github.com:odoo/{repo}.git', '-b', branch]
            try:
                subprocess.check_call(cmd)
            except subprocess.CalledProcessError as e:
                print(f"Failed to clone odoo/{repo}: {e}")
                continue

    # Create odoo.conf
    create_odoo_conf(project_dir, extra_params, submodules)

if __name__ == "__main__":
    main()