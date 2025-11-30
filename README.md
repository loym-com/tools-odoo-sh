How to use

```
ln -s src/user/loym-com/tools-odoo-sh/task ~/task

bash task help
```

How to edit inside odoo.sh

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
