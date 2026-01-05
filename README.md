# Inside odoo.sh

## How to use

```
ln -s src/user/loym-com/tools-odoo-sh/task ~/task

bash task help
```

## How to edit

```
cd ~/src/user/loym-com/tools-odoo-sh

# Replace https with git
git remote set-url origin git@github.com:loym-com/tools-odoo-sh.git

# checkout
git fetch origin
git checkout -b main-editable origin/main

# edit
git add <files>
git commit -m "My changes"

# pull
git fetch origin
git merge origin/main  # optional if remote main changed

# push
git push -u origin main-editable:main
```

# On localhost

```
cp settings_template.py settings.py

bash task help
```


# LOCALLY

Tools to test/develop odoo-sh projects locally with minimal disk usage.

## Local file structure

~/gh/git-provider/user/repo/branch (currently only github supported)

## Workflow

1. Clone odoo-sh repo into ~/gh/user/repo/branch using gitclone.py or git clone.
2. cd into the repo.
3. Run `python main.py <version>` to set up the local environment.

This will:
- Copy settings_template.py into .local/settings.py, and add the version.
- Clone odoo-sh submodules into relevant ~/gh/user/repo/branch destinations.
- Create .venv and install all dependencies. Includes odoo core if not odoo_core_in_submodules.
- Create symlinks in .local for each submodule (and odoo core if applicable).

## Usage

```bash
# Clone the odoo-sh project
python gitclone.py https://github.com/user/repo.git -b branch

# Or manually
git clone https://github.com/user/repo.git ~/gh/user/repo/branch

# cd into it
cd ~/gh/user/repo/branch

# Run setup
python /path/to/tools-odoo-sh/main/main.py 18.0

# Activate venv
source .venv/bin/activate

# Run odoo
odoo --config .local/odoo.conf
```

## Individual scripts

- `gitclone.py`: Clone repos with worktrees.
- `create_local_folder.py`: Create .local with symlinks (assumes submodules cloned).
- `create_venv.py`: Create venv and install requirements.
- `create_odoo_conf.py`: Create odoo.conf with addons paths.