import os
from os.path import abspath

import rich
import typer

from flowutils.utils import load_config, LinkConfig, save_config

app = typer.Typer()


@app.command()
def create():
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
def add(target_directory: str, name: str):
    """Add a link to the config file."""
    config = load_config()

    link: LinkConfig = LinkConfig(target=abspath(target_directory), name=name)
    config.links.append(link)
    save_config(config)

    rich.print(f"[blue]Link '{name}' added.")


@app.command(name="list")
def list_links():
    """List the links."""
    config = load_config()
    links = config.links
    if not links:
        rich.print("[blue]No links found.")
        return

    rich.print("[orange]Links:")
    for link in links:
        rich.print(f"[blue]{link.name} [green] -> {link.target}")
