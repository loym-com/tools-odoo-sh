# settings.py

from pathlib import Path

# Odoo.sh does not include odoo core in submodules.
# Locally, there are two possible setups:
# A) Include odoo core in submodules (default in project-odoo-sh). This is NOT compatible with odoo.sh!
# B) Clone to BASE_DIR/odoo/repo/version, e.g.
#    - BASE_DIR/gh/odoo/odoo/18.0
#    - BASE_DIR/gh/odoo/design-themes/18.0
#    - BASE_DIR/gh/odoo/industry/18.0
#    - BASE_DIR/gh/odoo/enterprise/18.0
ODOO_CORE_IS_IN_SUBMODULES = True

BASE_DIR = Path.home() / "src"
GITHUB_DIR = BASE_DIR / "gh"
PROJECT_DIR = Path(__file__).resolve().parents[1]
# PROJECT_VERSION = "18.0"
