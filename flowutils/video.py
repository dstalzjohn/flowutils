import os

import rich
import typer

from flowutils.audio import is_ffmpeg_installed
import subprocess

# for file in /pfad/zum/AVCHD/BDMV/STREAM/*.MTS; do ffmpeg -i "$file" -c:v libx264 -crf 23 -c:a aac -b:a 128k "${file%.*}.mp4"; done

app = typer.Typer()


@app.command()
def extract_avchd(container_file_path: str =
           typer.Argument(help="Location path of the avchd folder"),
           output_folder: str = typer.Argument(None, help="Location of the output folder")):
    """Convert mp3 file to m4a file."""
    if not is_ffmpeg_installed():
        rich.print("[red]ffmpeg is not installed.")
        return
    convert_avchd_to_mp4(container_file_path, output_folder)
    rich.print(f"[blue]MP4 file(s) created at: {output_folder}")


def convert_avchd_to_mp4(container_file_path: str, output_folder: str, codec='libx264', crf=23, audio_bitrate='128k'):
    """Convert avchd file to mp4 files"""
    os.makedirs(output_folder, exist_ok=True)
    stream_dir = os.path.join(container_file_path, 'BDMV', 'STREAM')

    if not os.path.exists(stream_dir):
        rich.print(f"Error: STREAM directory not found in {container_file_path}")
        return

    filenames = os.listdir(stream_dir)

    for idx, filename in enumerate(filenames):
        if filename.endswith('.MTS'):
            input_path = os.path.join(stream_dir, filename)
            output_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}.mp4")

            # Construct the FFmpeg command
            command = [
                'ffmpeg',
                '-i', input_path,
                '-c:v', codec,
                '-crf', str(crf),
                '-c:a', 'aac',
                '-b:a', audio_bitrate,
                output_path
            ]

            try:
                rich.print(f"[green]Starting with {idx}/{len(filenames)}[/green]")
                subprocess.run(command, check=True)
                rich.print(f"Successfully converted {filename}")
            except subprocess.CalledProcessError as e:
                rich.print(f"Error converting {filename}: {e}")

