import os
from os.path import dirname, isdir, join, abspath
from pathlib import Path

import git
import yaml
import typer
import rich

app = typer.Typer()


def get_config_path():
    """Get the path to the config file. If the FLOW_CONFIG environment variable is set, use that."""
    flow_config = os.environ.get("FLOW_CONFIG", "~/.flowutils/config.yaml")
    return os.path.expanduser(flow_config)


def load_config():
    """Load the config file."""
    config_path = get_config_path()
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def save_config(config):
    """Save the config file."""
    config_path = get_config_path()
    with open(config_path, "w") as f:
        yaml.dump(config, f)


@app.command()
def init(
    link_location: str = typer.Option(
        os.path.expanduser("~/Links"),
        prompt="Enter the link location",
        help="Location path of the links",
    ),
    project_location: str = typer.Option(
        os.path.expanduser("~/Projects"),
        prompt="Enter the project location",
        help="Location path of the projects",
    ),
    capture: bool = typer.Option(
        False,
        prompt="Capture existing projects?",
        help="Capture existing projects and add them to project names",
    ),
):
    """Initialize the config file."""
    config_path = get_config_path()
    config = {
        "link_location": link_location,
        "project_location": project_location,
        "project_names": [],
        "project_subdirs": [],
        "links": [],
        "git_repos": [],
    }

    if capture and isdir(project_location):
        projects = os.listdir(project_location)
        config["project_names"] = sorted([project for project in projects if
                                   isdir(join(project_location, project))
                                   and not project.startswith(".")])

    os.makedirs(dirname(config_path), exist_ok=True)
    save_config(config)

    rich.print(f"[blue]Config file created at: {config_path}")


@app.command()
def create_project_dirs():
    """Create the project directories."""
    config = load_config()

    project_location = config["project_location"]
    project_names = config["project_names"]
    project_subdirs = config["project_subdirs"]

    for name in project_names:
        for subdir in project_subdirs:
            dir_path = os.path.join(project_location, name, subdir)
            os.makedirs(dir_path, exist_ok=True)

    rich.print("[blue]Project directories created.")


@app.command()
def add_project(project: str):
    """Add a project to the config file."""
    config = load_config()

    project_names = config["project_names"]
    project_names.append(project)

    save_config(config)

    rich.print(f"[blue]Project '{project}' added.")


@app.command()
def create_links():
    """Create the links."""
    config = load_config()

    link_location = config["link_location"]
    links = config["links"]
    os.makedirs(link_location, exist_ok=True)
    for link in links:
        target = link["target"]
        name = link["name"]

        link_path = os.path.join(link_location, name)
        os.symlink(target, link_path)

    rich.print("[blue]Links created.")


@app.command()
def add_link(target_directory: str, name: str):
    """Add a link to the config file."""
    config = load_config()

    links = config["links"]
    links.append({"target": abspath(target_directory), "name": name})

    save_config(config)

    rich.print(f"[blue]Link '{name}' added.")


@app.command()
def collect_git_repos():
    """Collect the Git repositories."""
    config = load_config()

    project_location = config["project_location"]
    git_repos = []

    for root, dirs, files in os.walk(project_location):
        if ".git" in dirs:
            git_repo_path = Path(os.path.join(root, ".git"))
            git_repo_url = get_remote_url(str(git_repo_path))
            if git_repo_url:
                repo_info = {"file_location": str(git_repo_path), "url": git_repo_url}
                git_repos.append(repo_info)

    config["git_repos"] = git_repos
    save_config(config)

    rich.print(f"[blue]{len(git_repos)} Git repositories collected.")


def get_remote_url(repo_path):
    """Get the remote URL of a Git repository."""
    try:
        repo = git.Repo(repo_path, search_parent_directories=True)
        return repo.remotes.origin.url
    except git.InvalidGitRepositoryError:
        return None


@app.command()
def create_git_repos():
    """Create the Git repositories."""
    config = load_config()
    git_repos = config["git_repos"]

    for repo_info in git_repos:
        url = repo_info.get("url")
        file_location = repo_info.get("file_location")
        if url and file_location:
            if isdir(join(file_location, ".git")):
                continue
            try:
                git.Repo.clone_from(url, file_location)
                rich.print(f"[green]Git repository cloned from '{url}' to '{file_location}'.")
            except git.GitCommandError as e:
                rich.print(f"[red]An error occurred while cloning the repository from '{url}': {str(e)}")

    rich.print("[blue]Git repositories created.")


if __name__ == "__main__":
    app()
