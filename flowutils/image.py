"""Module for resizing images in a folder"""

import os
from typing import List
from PIL import Image
import rich
import typer

app = typer.Typer()


def resize_images(
    input_folder: str,
    output_folder: str,
    formats: List[str],
    max_size: int,
    quality: int,
    dry_run: bool = False,
):
    """Resize images in the input folder and save them to the output folder."""
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if any(filename.lower().endswith(fmt.lower()) for fmt in formats):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)

            if dry_run:
                rich.print(f"[blue]Would resize: {input_path} -> {output_path}")
            else:
                try:
                    with Image.open(input_path) as img:
                        img.thumbnail((max_size, max_size))
                        img.save(output_path, quality=quality, optimize=True)
                    rich.print(f"[green]Resized: {input_path} -> {output_path}")
                except Exception as e:
                    rich.print(f"[red]Error processing {input_path}: {str(e)}")


@app.command()
def resize(
    input_folder: str = typer.Argument(help="Input folder path"),
    output_folder: str = typer.Argument(help="Output folder path"),
    formats: List[str] = typer.Option(
        ["jpg", "jpeg", "png"], "--formats", "-f", help="Image formats to process"
    ),
    max_size: int = typer.Option(
        1024, "--size", "-s", help="Maximum size of the longer edge"
    ),
    quality: int = typer.Option(
        85, "--quality", "-q", help="Output image quality (0-95)"
    ),
    dry_run: bool = typer.Option(
        False, "--dry", "-d", help="Perform a dry run without actually resizing images"
    ),
):
    """Resize images in the input folder and save them to the output folder."""
    input_folder = os.path.expanduser(input_folder)
    output_folder = os.path.expanduser(output_folder)

    if not os.path.exists(input_folder):
        rich.print(f"[red]Input folder not found: {input_folder}")
        return

    color = "blue" if dry_run else "green"
    rich.print(
        f"[{color}]{'Dry run: ' if dry_run else ''}Resizing images in {input_folder}"
    )
    rich.print(f"[{color}]Output folder: {output_folder}")
    rich.print(f"[{color}]Formats: {', '.join(formats)}")
    rich.print(f"[{color}]Max size: {max_size}")
    rich.print(f"[{color}]Quality: {quality}")

    resize_images(input_folder, output_folder, formats, max_size, quality, dry_run)


if __name__ == "__main__":
    app()
