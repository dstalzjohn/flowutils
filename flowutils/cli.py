import os
from os.path import dirname, isdir, join, abspath, expanduser
from pathlib import Path

import git
import yaml
import typer
import rich
from rich.pretty import Pretty
from rich.panel import Panel
from pydantic import BaseModel

app = typer.Typer()


class LinkConfig(BaseModel):
    """Link config model."""

    target: str
    name: str


class GitRepoConfig(BaseModel):
    """Git repo config model."""

    url: str
    file_location: str


class FlowConfig(BaseModel):
    """Flow config model."""

    link_location: str = "~/Links"
    project_location: str = "~/Projects"
    project_names: list[str] = []
    project_subdirs: list[str] = []
    links: list[LinkConfig] = []
    git_repos: list[GitRepoConfig] = []

    def get_project_location(self) -> str:
        return expanduser(self.project_location)

    def get_link_location(self) -> str:
        return expanduser(self.link_location)


def get_config_path():
    """Get the path to the config file. If the FLOW_CONFIG environment variable is set, use that."""
    flow_config = os.environ.get("FLOW_CONFIG", "~/.flowutils/config.yaml")
    return os.path.expanduser(flow_config)


def load_config() -> FlowConfig:
    """Load the config file."""
    config_path = get_config_path()
    with open(config_path, "r") as f:
        dict_conf = yaml.safe_load(f)
    return FlowConfig(**dict_conf)


def save_config(config: FlowConfig):
    """Save the config file."""
    config_path = get_config_path()
    with open(config_path, "w") as f:
        yaml.dump(config.model_dump(), f)


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
    config = FlowConfig(link_location=link_location, project_location=project_location)

    if capture and isdir(config.get_project_location()):
        projects = os.listdir(config.get_project_location())
        config.project_names = sorted(
            [
                project
                for project in projects
                if isdir(join(project_location, project))
                and not project.startswith(".")
            ]
        )

    os.makedirs(dirname(config_path), exist_ok=True)
    save_config(config)

    rich.print(f"[blue]Config file created at: {config_path}")


@app.command()
def show_projects():
    """Show the projects."""
    config = load_config()
    pretty = Pretty(config.project_names)
    panel = Panel(pretty, title="Projects")
    rich.print(panel)


@app.command()
def capture_projects():
    config = load_config()
    projects = os.listdir(config.get_project_location())
    config.project_names = sorted(
        [
            project
            for project in projects
            if isdir(join(config.get_project_location(), project))
            and not project.startswith(".")
        ]
    )
    save_config(config)
    rich.print(f"[blue]Captured {len(config.project_names)} projects.")


@app.command()
def create_project_dirs():
    """Create the project directories."""
    config = load_config()

    project_location = config.get_project_location()

    for name in config.project_names:
        for subdir in config.project_subdirs:
            dir_path = os.path.join(project_location, name, subdir)
            os.makedirs(dir_path, exist_ok=True)
            rich.print(f"[yellow]Created directory '{dir_path}'.")

    rich.print("[blue]Project directories created.")


@app.command()
def add_project(project: str):
    """Add a project to the config file."""
    config = load_config()
    if project in config.project_names:
        rich.print(f"[yellow]Project '{project}' already exists.")
        return
    config.project_names.append(project)
    save_config(config)

    rich.print(f"[blue]Project '{project}' added.")


@app.command()
def create_links():
    """Create the links."""
    config = load_config()

    link_location = config.get_link_location()
    os.makedirs(link_location, exist_ok=True)
    link: LinkConfig
    for link in config.links:
        link_path = os.path.join(link_location, link.name)
        os.symlink(link.target, link_path)

    rich.print("[blue]Links created.")


@app.command()
def add_link(target_directory: str, name: str):
    """Add a link to the config file."""
    config = load_config()

    link: LinkConfig = LinkConfig(target=abspath(target_directory), name=name)
    config.links.append(link)
    save_config(config)

    rich.print(f"[blue]Link '{name}' added.")


@app.command()
def collect_git_repos():
    """Collect the Git repositories."""
    config = load_config()

    project_location = config.get_project_location()
    git_repos = []

    for root, dirs, files in os.walk(project_location):
        if ".git" in dirs:
            git_repo_path = Path(os.path.join(root, ".git"))
            git_repo_url = get_remote_url(str(git_repo_path))
            if git_repo_url:
                repo_info = GitRepoConfig(
                    file_location=str(git_repo_path), url=git_repo_url
                )
                git_repos.append(repo_info)
                rich.print(
                    f"[green]Git repository found at '{git_repo_path}' with url: {git_repo_url}."
                )

    config.git_repos = git_repos
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

    for repo_info in config.git_repos:
        if isdir(join(repo_info.file_location, ".git")):
            rich.print(
                f"[yellow]Git repository already exists at '{repo_info.file_location}'."
            )
            continue
        try:
            git.Repo.clone_from(repo_info.url, repo_info.file_location)
            rich.print(
                f"[green]Git repository cloned from '{repo_info.url}' to '{repo_info.file_location}'."
            )
        except git.GitCommandError as e:
            rich.print(
                f"[red]An error occurred while cloning the repository from '{repo_info.url}': {str(e)}"
            )

    rich.print("[blue]Git repositories created.")


if __name__ == "__main__":
    app()
