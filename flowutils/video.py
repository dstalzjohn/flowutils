import os

import rich
import typer

from flowutils.audio import is_ffmpeg_installed
import subprocess


app = typer.Typer()


@app.command()
def extract_avchd(
    container_file_path: str = typer.Argument(help="Location path of the avchd folder"),
    output_folder: str = typer.Argument(None, help="Location of the output folder"),
):
    """Exctracts mp3 videos from a avchd container file"""
    if not is_ffmpeg_installed():
        rich.print("[red]ffmpeg is not installed.")
        return
    convert_avchd_to_mp4(container_file_path, output_folder)
    rich.print(f"[blue]MP4 file(s) created at: {output_folder}")


def convert_avchd_to_mp4(
    container_file_path: str,
    output_folder: str,
    codec="libx264",
    crf=23,
    audio_bitrate="128k",
):
    """Convert avchd file to mp4 files"""
    os.makedirs(output_folder, exist_ok=True)
    stream_dir = os.path.join(container_file_path, "BDMV", "STREAM")

    if not os.path.exists(stream_dir):
        rich.print(f"Error: STREAM directory not found in {container_file_path}")
        return

    filenames = os.listdir(stream_dir)

    for idx, filename in enumerate(filenames):
        if filename.endswith(".MTS"):
            input_path = os.path.join(stream_dir, filename)
            output_path = os.path.join(
                output_folder, f"{os.path.splitext(filename)[0]}.mp4"
            )

            # Construct the FFmpeg command
            command = [
                "ffmpeg",
                "-i",
                input_path,
                "-c:v",
                codec,
                "-crf",
                str(crf),
                "-c:a",
                "aac",
                "-b:a",
                audio_bitrate,
                output_path,
            ]

            try:
                rich.print(f"[green]Starting with {idx}/{len(filenames)}[/green]")
                subprocess.run(command, check=True)
                rich.print(f"Successfully converted {filename}")
            except subprocess.CalledProcessError as e:
                rich.print(f"Error converting {filename}: {e}")


@app.command()
def extract_audio_as_mp3(
    video_file_path: str = typer.Argument(help="Path to the video file"),
    output_file: str = typer.Argument(help="Path to the output mp3 file"),
):
    """Extracts audio from a video file and saves it as mp3"""
    if not is_ffmpeg_installed():
        rich.print("[red]ffmpeg is not installed.")
        return
    convert_video_to_mp3(video_file_path, output_file)
    rich.print(f"[blue]MP3 audio file created at: {output_file}")


def convert_video_to_mp3(video_file_path: str, output_file: str, audio_bitrate="192k"):
    """Convert video file to mp3"""
    output_dir = os.path.dirname(output_file)
    if len(output_dir) > 0:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Construct the FFmpeg command
    command = [
        "ffmpeg",
        "-i",
        video_file_path,
        "-q:a",
        "0",
        "-map",
        "a",
        "-b:a",
        audio_bitrate,
        output_file,
    ]

    try:
        rich.print(f"[green]Extracting audio from {video_file_path}[/green]")
        subprocess.run(command, check=True)
        rich.print(f"Successfully extracted audio to {output_file}")
    except subprocess.CalledProcessError as e:
        rich.print(f"Error extracting audio from {video_file_path}: {e}")
