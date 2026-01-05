# settings.py

from pathlib import Path

project_version = "18.0"

project_root = Path(__file__).resolve().parents[3]

# github_root is relevant only when odoo core is NOT in submodules.
github_root = "~/gh"

# Odoo.sh does not include odoo core in submodules.
# Locally, there are two possible setups:
# A) Include odoo core in submodules (default in project-odoo-sh). This is NOT compatible with odoo.sh!
# B) Clone to github_root/odoo/repo/version, e.g.
#    - github_root/odoo/odoo/18.0
#    - github_root/odoo/design-themes/18.0
#    - github_root/odoo/industry/18.0
#    - github_root/odoo/enterprise/18.0
odoo_core_in_submodules = True
