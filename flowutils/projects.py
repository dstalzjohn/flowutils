import os
from os.path import isdir, join

import rich
import typer
from rich.panel import Panel
from rich.pretty import Pretty

from flowutils.utils import load_config, save_config

app = typer.Typer()


@app.command(name="list")
def list_projects():
    """Show the projects."""
    config = load_config()
    pretty = Pretty(config.project_names)
    panel = Panel(pretty, title="Projects")
    rich.print(panel)


@app.command()
def capture():
    """Capture the projects and add them to the config file."""
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
def create():
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
def add(project: str):
    """Add a project to the config file."""
    config = load_config()
    if project in config.project_names:
        rich.print(f"[yellow]Project '{project}' already exists.")
        return
    config.project_names.append(project)
    save_config(config)

    rich.print(f"[blue]Project '{project}' added.")
