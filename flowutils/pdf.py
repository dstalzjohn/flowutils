"""
Module for reducing the size of scanned PDF files.

This script provides functionality to compress scanned PDF files,
reducing their file size while maintaining reasonable quality.
"""

import os
import subprocess
import typer
from rich import print as rprint

app = typer.Typer()


def compress_pdf(input_path: str, output_path: str, dpi: int = 150) -> None:
    """
    Compress a scanned PDF file.

    Args:
        input_path (str): Path to the input PDF file.
        output_path (str): Path where the compressed PDF will be saved.
        dpi (int, optional): DPI for the output file. Defaults to 150.

    Raises:
        subprocess.CalledProcessError: If the ghostscript command fails.
    """
    try:
        subprocess.run(
            [
                "gs",
                "-sDEVICE=pdfwrite",
                "-dCompatibilityLevel=1.4",
                "-dPDFSETTINGS=/screen",
                "-dNOPAUSE",
                "-dQUIET",
                "-dBATCH",
                f"-r{dpi}",
                f"-sOutputFile={output_path}",
                input_path,
            ],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        rprint(f"[red]Error compressing PDF: {e}")
        raise


@app.command()
def compress(
    input_file: str = typer.Argument(..., help="Path to the input PDF file"),
    output_file: str = typer.Option(None, help="Path for the output compressed PDF"),
    dpi: int = typer.Option(150, help="DPI for the output file"),
):
    """
    Compress a scanned PDF file and save the result.

    If no output file is specified, the compressed file will be saved with
    '_compressed' appended to the original filename.
    """
    if not os.path.exists(input_file):
        rprint(f"[red]Input file not found: {input_file}")
        return

    if output_file is None:
        base, ext = os.path.splitext(input_file)
        output_file = f"{base}_compressed{ext}"

    try:
        compress_pdf(input_file, output_file, dpi)
        rprint(f"[green]PDF compressed successfully. Saved as: {output_file}")
    except subprocess.CalledProcessError:
        rprint("[red]Failed to compress PDF.")
