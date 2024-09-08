"""module for config commands"""
import os
from datetime import datetime

import rich
import typer

from flowutils.utils import get_config_path

app = typer.Typer()


@app.command()
def backup():
    """Backup the config file with a timestamp."""
    config_path = get_config_path()
    if not os.path.exists(config_path):
        rich.print("[red]Config file not found.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{config_path}.{timestamp}.bak"

    try:
        with open(config_path, "r") as source, open(backup_path, "w") as target:
            target.write(source.read())
        rich.print(f"[green]Config backed up to: {backup_path}")
    except IOError as e:
        rich.print(f"[red]Error backing up config: {str(e)}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
