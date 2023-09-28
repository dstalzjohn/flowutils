import os
from os.path import isdir, join, dirname
from pathlib import Path

import git
import rich
import typer

from flowutils.utils import load_config, GitRepoConfig, save_config

app = typer.Typer()


@app.command()
def collect():
    """Collect the Git repositories."""
    config = load_config()

    project_location = config.get_project_location()
    git_repos = config.git_repos

    for root, dirs, files in os.walk(project_location):
        if ".git" in dirs:
            git_repo_path = Path(os.path.join(root, ".git"))
            git_repo_url = get_remote_url(str(git_repo_path))
            if git_repo_url:
                repo_info = GitRepoConfig(
                    file_location=str(git_repo_path), url=git_repo_url
                )
                if repo_info not in git_repos:
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
    except (git.InvalidGitRepositoryError, AttributeError):
        return None


@app.command(name="list")
def list_repos():
    """List the Git repositories."""
    config = load_config()
    git_repos = config.git_repos
    if not git_repos:
        rich.print("[blue]No Git repositories found.")
        return

    rich.print("[orange]Git repositories:")
    for repo in git_repos:
        rich.print(f"[blue]{repo.file_location} [green] -> {repo.url}")


@app.command()
def create():
    """Create the Git repositories."""
    config = load_config()

    for repo_info in config.git_repos:
        if isdir(repo_info.file_location):
            rich.print(
                f"[yellow]Git repository already exists at '{repo_info.file_location}'."
            )
            continue
        try:
            git.Repo.clone_from(repo_info.url, dirname(repo_info.file_location))
            rich.print(
                f"[green]Git repository cloned from '{repo_info.url}' to '{repo_info.file_location}'."
            )
        except git.GitCommandError as e:
            rich.print(
                f"[red]An error occurred while cloning the repository from '{repo_info.url}': {str(e)}"
            )

    rich.print("[blue]Git repositories created.")
