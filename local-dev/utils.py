import configparser
import re
import sys
from pathlib import Path
from pprint import pprint


def get_settings(project_dir):
    """
    Dynamically insert the local directory containing settings.py into sys.path and return the settings module.

    Args:
        project_dir (Path): The root directory of the project.

    Returns:
        module: The loaded settings module.

    Raises:
        FileNotFoundError: If the settings.py file is not found.
    """
    settings_path = project_dir / ".local" / "settings.py"
    if not settings_path.exists():
        raise FileNotFoundError(f"Settings file not found: {settings_path}")

    settings_dir = settings_path.parent
    sys.path.insert(0, str(settings_dir))
    import settings  # Dynamically import the settings module
    return settings

def get_submodules(project_dir):
    submodules = []
    gitmodules_path = project_dir / ".gitmodules"
    if not gitmodules_path.exists():
        return submodules

    config = configparser.ConfigParser()
    config.read(gitmodules_path)

    for section in config.sections():
        if section.startswith('submodule '):
            # Extract name from [submodule "name"]
            name_match = re.search(r'submodule "(.*?)"', section)
            if name_match:
                sm = dict(config[section])
                sm['name'] = name_match.group(1)
                submodules.append(sm)
    # Sort submodules by path
    submodules.sort(key=lambda sm: sm['path'])
    return submodules

def get_repos(project_dir, submodules):
    """
    Get submodules and odoo core repos.
    Return list of dicts with keys: url, branch, repo_dir, search_dir
    """
    repos = []
    for sm in submodules:
        sm["repo_dir"] = get_repo_dir(sm, project_dir)
        repos.append(sm)
    repos.extend(get_odoo_core_repos(project_dir))
    for repo in repos:
        url_name = repo['url'][4:-4]  # remove 'git@' and '.git'
        dir_name = f"{sanitize_string(url_name)}-{repo['branch']}"
        repo['search_dir'] = project_dir / ".local" / "search" / dir_name
    return repos

def get_odoo_core_repos(project_dir):
    settings = get_settings(project_dir)
    from settings import ENTERPRISE

    names = ['odoo', 'design-themes', 'industry']
    if ENTERPRISE:
        names.append('enterprise')
    repos = [
        {
            'url': f"git@github.com:odoo/{name}.git",
            "branch": settings.ODOO_VERSION,
            'repo_dir': settings.GITHUB_DIR / 'odoo' / name / settings.ODOO_VERSION,
        }
        for name in names
    ]
    return repos

def get_repo_dir(submodule, project_dir):
    settings = get_settings(project_dir)
    branch = submodule['branch']
    url = submodule['url']

    m = re.search(r'(?P<provider>github\.com|gitlab\.com|bitbucket\.org)[:/](?P<user>[^/]+)/(?P<repo>[^/]+)\.git$', url)
    if not m:
        raise ValueError(f"Cannot parse repo URL: {url}")

    provider, user, repo = m.group("provider"), m.group("user"), m.group("repo")
    if provider == "github.com":
        repo_dir= settings.GITHUB_DIR / user / repo / branch
    else:
        raise ValueError(f"Unsupported provider: {provider}")
    return repo_dir

def sanitize_string(input_string):
    """
    Replace special characters in a string with '-'.

    Args:
        input_string (str): The string to sanitize.

    Returns:
        str: The sanitized string.
    """
    return re.sub(r'[^\w.-]', '-', str(input_string))

