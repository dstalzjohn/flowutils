"""module for sorting commands"""
import os
import shutil
from typing import List

import rich
import typer

from flowutils.utils import (
    load_config,
    SortingRuleConfig,
    SortFolderConfig,
    save_config,
)

app = typer.Typer()


def sort_folder(
    folder_path: str, rules: List[SortingRuleConfig], dry_run: bool = False
):
    """Sort files in a folder based on the given rules."""
    for rule in rules:
        rich.print(f"[pale_turquoise1]{rule.sub_folder_name}[/pale_turquoise1]")
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                if any(
                    keyword.lower() in filename.lower() for keyword in rule.contain_list
                ):
                    target_folder = os.path.join(folder_path, rule.sub_folder_name)
                    target_path = os.path.join(target_folder, filename)
                    if dry_run:
                        rich.print(
                            f"[blue]Would move: {file_path} -> {rule.sub_folder_name}"
                        )
                    else:
                        os.makedirs(target_folder, exist_ok=True)
                        shutil.move(file_path, target_path)
                        rich.print(
                            f"[green]Moved: {file_path} -> {rule.sub_folder_name}"
                        )



@app.command()
def run(
    dry_run: bool = typer.Option(
        False, "--dry", "-d", help="Perform a dry run without actually moving files"
    )
):
    """Sort files in configured folders."""
    config = load_config()

    for folder_config in config.sort.folder_configs:
        folder_path = os.path.expanduser(folder_config.target_folder)
        if os.path.exists(folder_path):
            color = "blue" if dry_run else "green"
            rich.print(
                f"[{color}]{'Dry run: ' if dry_run else ''}Sorting files in {folder_path}"
            )
            sort_folder(folder_path, folder_config.rules, dry_run)
        else:
            rich.print(f"[red]Folder not found: {folder_path}")


@app.command()
def add_rule(target_folder: str, sub_folder_name: str, keywords: List[str]):
    """Add a sorting rule to the config file."""
    config = load_config()

    new_rule = SortingRuleConfig(sub_folder_name=sub_folder_name, contain_list=keywords)

    for folder_config in config.sort.folder_configs:
        if folder_config.target_folder == target_folder:
            folder_config.rules.append(new_rule)
            save_config(config)
            rich.print(f"[blue]Rule added for {target_folder}")
            return

    new_folder_config = SortFolderConfig(target_folder=target_folder, rules=[new_rule])
    config.sort.folder_configs.append(new_folder_config)
    save_config(config)
    rich.print(f"[blue]New folder config and rule added for {target_folder}")


@app.command(name="list")
def list_rules():
    """List all sorting rules."""
    config = load_config()

    if not config.sort.folder_configs:
        rich.print("[blue]No sorting rules found.")
        return

    for folder_config in config.sort.folder_configs:
        rich.print(f"[orange]Rules for {folder_config.target_folder}:")
        for rule in folder_config.rules:
            rich.print(
                f"[blue]  {rule.sub_folder_name}: {', '.join(rule.contain_list)}"
            )


if __name__ == "__main__":
    app()
