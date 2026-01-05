#!/usr/bin/env python3
import sys
import re
from pathlib import Path

def parse_gitmodules(gitmodules_path):
    submodules = []
    if not gitmodules_path.exists():
        return submodules

    current = {}
    with open(gitmodules_path, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("[submodule"):
                if current:
                    submodules.append(current)
                    current = {}
                match = re.match(r'\[submodule "(.*?)"\]', line)
                if match:
                    current['name'] = match.group(1)
            elif "=" in line:
                key, value = map(str.strip, line.split("=", 1))
                current[key] = value
        if current:
            submodules.append(current)
    return submodules

def parse_repo(url):
    if 'github.com' not in url:
        raise ValueError(f"URL {url} is not from github.com")
    m = re.search(r'[:/](?P<user>[^/]+)/(?P<repo>[^/]+)\.git$', url)
    if not m:
        raise ValueError(f"Cannot parse repo URL: {url}")
    return m.group("user"), m.group("repo")

def main():
    if len(sys.argv) < 2:
        print("Usage: python 2_submodule_paths.py <PROJECT_DIR>")
        sys.exit(1)

    project_dir = Path(sys.argv[1])
    gitmodules_path = project_dir / ".gitmodules"
    local_dir = project_dir / ".local"

    # Import settings from .local
    sys.path.insert(0, str(local_dir))
    from settings import GITHUB_DIR

    submodules = parse_gitmodules(gitmodules_path)
    paths = []
    for sm in submodules:
        url = sm['url']
        user, repo = parse_repo(url)
        branch = sm.get('branch', 'main')
        path = GITHUB_DIR / user / repo / branch
        paths.append(path)

    # Write to .local/submodule_paths.py
    output_file = local_dir / "submodule_paths.py"
    with open(output_file, "w") as f:
        f.write("from pathlib import Path\n\n")
        f.write("paths = [\n")
        for path in paths:
            f.write(f'    Path("{path}"),\n')
        f.write("]\n")

    print(f"Submodule local paths written to {output_file}")

if __name__ == "__main__":
    main()