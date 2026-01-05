#!/usr/bin/env python3
"""
0_install.py - Install system dependencies for Odoo development on Debian-based systems
"""

import subprocess

def run_cmd(cmd):
    """Run a shell command"""
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

def install_dependencies():
    run_cmd(["sudo", "apt-get", "update"])
    run_cmd(["sudo", "apt-get", "install", "-y", "--no-install-recommends",
             "postgresql", "git", "python3-dev", "build-essential",
             "libpq-dev", "libldap2-dev", "libsasl2-dev", "python3-venv"])

if __name__ == "__main__":
    print("Installing system dependencies for Odoo development...")
    install_dependencies()
    print("System dependencies installed successfully.")
    print("You can now run the Python scripts to set up your Odoo environment.")