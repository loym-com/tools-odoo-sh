#!/usr/bin/env python3
import os
import re
import sys

from settings import odoo_core_in_submodules
from settings import github_root
from settings import project_root

"""
USAGE
python create_odoo_conf.py key1=value1 key2=value2
EXAMPLE
python create_odoo_conf.py db_user=odoo db_port=5432
"""

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

def create_odoo_conf(extra_params):

    # Default configurations
    defaults = {
        "admin_passwd": "admin",
        "auth_admin_passkey_password": "admin",
        "dbfilter": ".*",
        "db_host": "localhost",
        "db_name": project_root.name,
        "db_port": "5432",
        "db_user": "odoo",
        "db_password": "odoo",
        "http_interface": "127.0.0.1",
        "http_port": "8069",
        "log_level": "info",
        "xmlrpc_port": "8069"
    }

    # Override defaults with user-provided key=value
    for kv in extra_params:
        if '=' in kv:
            key, value = kv.split('=', 1)
            defaults[key] = value

    # Parse submodules from .gitmodules (next to odoo.conf)
    gitmodules_file = os.path.join(project_root, ".gitmodules")
    submodule_paths = parse_gitmodules(gitmodules_file)
    submodule_paths_abs = [os.path.join(project_root, p) for p in submodule_paths]

    # Sort submodules alphabetically (capital-sensitive)
    submodule_paths_abs.sort()

    # Fixed folders at the very end
    if odoo_core_in_submodules:
        fixed_paths_abs = []
    else:
        fixed_paths_abs = [
            os.path.join(odoo_core_repos_root, "odoo"),
            os.path.join(odoo_core_repos_root, "enterprise"),
            os.path.join(odoo_core_repos_root, "design-themes"),
            os.path.join(odoo_core_repos_root, "industry")
        ]

    # Combine all addons
    all_addons = submodule_paths_abs + fixed_paths_abs

    # Ensure that paths ending with "odoo" get "/addons" appended
    all_addons = [p + "/addons" if p.endswith("odoo") else p for p in all_addons]

    # Format addons_path with line breaks and indentation
    addons_path_str = ",\n              ".join(all_addons)

    # Write odoo.conf
    local_folder = os.path.join(project_root, ".local")
    os.makedirs(local_folder, exist_ok=True)
    conf_file = os.path.join(local_folder, "odoo.conf")
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
        print("Usage: python localhost.py <version> [key=value ...]")
        sys.exit(1)

    extra_params = sys.argv[1:]
    create_odoo_conf(extra_params)

if __name__ == "__main__":
    main()
