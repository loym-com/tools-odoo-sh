#!/usr/bin/env python3
import os
import re
import sys

"""
USAGE
python create_odoo_conf.py version key1=value1 key2=value2
EXAMPLE
python create_odoo_conf.py 18 db_user=odoo db_port=5432
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

def create_odoo_conf(version, extra_params):
    # Folder of the script
    script_folder = os.path.dirname(os.path.abspath(__file__))

    # odoo.conf folder = two levels above script
    odoo_conf_folder = os.path.abspath(os.path.join(script_folder, "../.."))

    # gh folder with fixed folders
    gh_folder = os.path.expanduser(f"~/loym/gh/{version}")

    # Default configurations
    defaults = {
        "admin_passwd": "admin",
        "db_host": "localhost",
        "db_port": "5432",
        "db_user": "odoo",
        "db_password": "odoo",
        "xmlrpc_port": str(int(version) * 1000)
    }

    # Override defaults with user-provided key=value
    for kv in extra_params:
        if '=' in kv:
            key, value = kv.split('=', 1)
            defaults[key] = value

    # Parse submodules from .gitmodules (next to odoo.conf)
    gitmodules_file = os.path.join(odoo_conf_folder, ".gitmodules")
    submodule_paths = parse_gitmodules(gitmodules_file)
    submodule_paths_abs = [os.path.join(odoo_conf_folder, p) for p in submodule_paths]

    # Sort submodules alphabetically (capital-sensitive)
    submodule_paths_abs.sort()

    # Fixed folders at the very end
    fixed_paths_abs = [
        os.path.join(gh_folder, "enterprise"),
        os.path.join(gh_folder, "design-themes"),
        os.path.join(gh_folder, "industry")
    ]

    # Combine all addons
    all_addons = submodule_paths_abs + fixed_paths_abs

    # Format addons_path with line breaks and indentation
    addons_path_str = ",\n              ".join(all_addons)

    # Write odoo.conf
    conf_file = os.path.join(odoo_conf_folder, "odoo.conf")
    os.makedirs(os.path.dirname(conf_file), exist_ok=True)
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

    version = sys.argv[1]
    extra_params = sys.argv[2:]
    create_odoo_conf(version, extra_params)

if __name__ == "__main__":
    main()
