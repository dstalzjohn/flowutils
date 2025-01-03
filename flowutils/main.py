import os
from os.path import dirname, isdir, join

import typer
import rich
from flowutils import (
    projects,
    links,
    repos,
    audio,
    video,
    sort,
    config,
    url,
    pdf,
    image,
)

from flowutils.utils import FlowConfig, get_config_path, save_config

app = typer.Typer()
app.add_typer(projects.app, name="projects")
app.add_typer(links.app, name="links")
app.add_typer(repos.app, name="repos")
app.add_typer(audio.app, name="audio")
app.add_typer(video.app, name="video")
app.add_typer(sort.app, name="sort")
app.add_typer(config.app, name="config")
app.add_typer(url.app, name="url")
app.add_typer(pdf.app, name="pdf")
app.add_typer(image.app, name="image")


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
    # check if config file already exists
    if os.path.isfile(config_path):
        rich.print(f"[red]Config file already exists at: {config_path}")
        return
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


if __name__ == "__main__":
    app()
