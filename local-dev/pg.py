#!/usr/bin/env python3
"""
pg.py - Create PostgreSQL user for Odoo using settings from .local/odoo.conf
"""

import subprocess
import sys
from pathlib import Path
import configparser

def run_psql(cmd):
    """Run psql command as postgres user"""
    full_cmd = ["sudo", "-u", "postgres", "psql", "-c", cmd]
    subprocess.run(full_cmd, check=True)

def create_user(db_user, db_password):
    """Create PostgreSQL user with createdb privilege"""
    print(f"Creating PostgreSQL user '{db_user}'...")
    run_psql(f"CREATE USER {db_user} WITH PASSWORD '{db_password}';")
    run_psql(f"ALTER USER {db_user} CREATEDB;")
    print(f"User '{db_user}' created successfully with createdb privilege.")

def main():
    if len(sys.argv) < 2:
        print("Usage: python pg.py <PROJECT_DIR>")
        sys.exit(1)

    project_dir = Path(sys.argv[1])
    odoo_conf = project_dir / ".local" / "odoo.conf"

    if not odoo_conf.exists():
        print(f"odoo.conf not found at {odoo_conf}")
        sys.exit(1)

    # Parse odoo.conf
    config = configparser.ConfigParser()
    config.read(odoo_conf)

    if 'options' not in config:
        print("Invalid odoo.conf: no [options] section")
        sys.exit(1)

    db_user = config['options'].get('db_user')
    db_password = config['options'].get('db_password')

    if not db_user or not db_password:
        print("db_user or db_password not found in odoo.conf")
        sys.exit(1)

    create_user(db_user, db_password)

if __name__ == "__main__":
    main()