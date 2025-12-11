# settings.py
#
# Odoo.sh does not include odoo core in submodules.
# Locally, there are two possible setups:
# A) Include odoo core in submodules (default in project-odoo-sh)
# B) Clone to github_root/version/odoo, e.g.
#    - github_root/18/odoo/odoo
#    - github_root/18/odoo/design-themes
#    - github_root/18/odoo/industry
#    - github_root/18/odoo/enterprise
odoo_core_in_submodules = True

# github_root is relevant only when odoo core is NOT in submodules.
github_root = "~/gh"
