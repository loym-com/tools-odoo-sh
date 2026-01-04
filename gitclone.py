#!/usr/bin/env python3
"""
gitclone.py – lightweight Git clone with per-branch worktrees.
- Default branch gets its own folder with .git
- Other branches get worktrees
- Symlink from USER/REPO/.git -> USER/REPO/default_branch/.git
- Shallow clone (--depth 1)
"""

import argparse
import subprocess
import sys
from pathlib import Path
import re
import os

def run(cmd, cwd=None, capture=False):
    if capture:
        return subprocess.check_output(cmd, cwd=cwd, text=True).strip()
    subprocess.check_call(cmd, cwd=cwd)

def parse_repo(url: str):
    m = re.search(r'[:/](?P<user>[^/]+)/(?P<repo>[^/]+)\.git$', url)
    if not m:
        raise ValueError(f"Cannot parse repo URL: {url}")
    return m.group("user"), m.group("repo")

def get_default_branch(repo_url: str) -> str:
    """Get default branch from GitHub origin without cloning"""
    output = run(["git", "ls-remote", "--symref", repo_url, "HEAD"], capture=True)
    for line in output.splitlines():
        if line.startswith("ref:"):
            return line.split()[1].replace("refs/heads/", "")
    raise RuntimeError("Could not determine default branch")

def main():
    parser = argparse.ArgumentParser(description="Clone Git repo with per-branch worktrees")
    parser.add_argument("repo", help="Git repository URL")
    parser.add_argument("-b", "--branch", help="Branch to check out (optional)")
    args = parser.parse_args()

    try:
        user, repo_name = parse_repo(args.repo)
    except ValueError as e:
        print(e, file=sys.stderr)
        sys.exit(1)

    base = Path.home() / "gh" / user / repo_name
    base.mkdir(parents=True, exist_ok=True)

    # Determine default branch first
    default_branch = get_default_branch(args.repo)

    # Which branch to checkout
    branch = args.branch or default_branch
    print(f"Branch to checkout: {branch} (default branch: {default_branch})")

    # --- Handle default branch ---
    default_branch_path = base / default_branch
    if not default_branch_path.exists():
        print(f"Cloning default branch '{default_branch}' into {default_branch_path} (shallow)...")
        run([
            "git", "clone",
            "--branch", default_branch,
            "--depth", "1",
            args.repo,
            str(default_branch_path)
        ])
    else:
        print(f"Default branch folder exists: {default_branch_path}")

    # Symlink USER/REPO/.git -> default_branch/.git
    git_symlink = base / ".git"
    if not git_symlink.exists():
        print(f"Creating symlink: {git_symlink} -> {default_branch_path}/.git")
        git_symlink.symlink_to(default_branch_path / ".git", target_is_directory=True)

    # --- Handle other branches ---
    if branch != default_branch:
        worktree_path = base / branch
        if not worktree_path.exists():
            print(f"Adding worktree for branch '{branch}' at {worktree_path} (shallow)...")
            run([
                "git", "worktree", "add", str(worktree_path), branch
            ], cwd=default_branch_path)
        else:
            print(f"Worktree already exists: {worktree_path}")
        os.chdir(worktree_path)
    else:
        os.chdir(default_branch_path)

    print(f"Checked out worktree: {Path.cwd()}")

if __name__ == "__main__":
    main()
