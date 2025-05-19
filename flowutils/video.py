import os

import rich
import typer

import yaml

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


def _format_time_for_ffmpeg(time_str: str) -> str:
    """
    Converts a flexible time string (e.g., "ss", "mm:ss", "hh:mm:ss")
    into the "HH:MM:SS" format required by ffmpeg.
    """
    time_str = str(time_str)  # Ensure it's a string, in case YAML parsed numbers
    parts = [int(p) for p in time_str.split(":")]

    if len(parts) == 1:  # seconds
        h, m, s = 0, 0, parts[0]
    elif len(parts) == 2:  # minutes:seconds
        h, m, s = 0, parts[0], parts[1]
    elif len(parts) == 3:  # hours:minutes:seconds
        h, m, s = parts[0], parts[1], parts[2]
    else:
        raise ValueError(
            f"Invalid time format: '{time_str}'. Expected 'ss', 'mm:ss', or 'hh:mm:ss'."
        )
    return f"{h:02d}:{m:02d}:{s:02d}"


def cut_video_into_scenes(
    input_video_path: str, cut_yaml_path: str, output_folder: str
):
    """
    Extracts scenes from the input video based on definitions in a YAML file
    and saves them to the output folder.
    """
    try:
        os.makedirs(output_folder, exist_ok=True)
    except OSError as e:
        rich.print(f"[red]Error creating output directory {output_folder}: {e}[/red]")
        return

    try:
        with open(cut_yaml_path, "r") as f:
            scenes_data = yaml.safe_load(f)
        if not isinstance(scenes_data, list):
            rich.print(
                f"[red]Error: Content of YAML file '{cut_yaml_path}' is not a list of scenes.[/red]"
            )
            return
    except FileNotFoundError:
        rich.print(f"[red]Error: Cut YAML file not found at '{cut_yaml_path}'[/red]")
        return
    except yaml.YAMLError as e:
        rich.print(f"[red]Error parsing YAML file '{cut_yaml_path}': {e}[/red]")
        return
    except Exception as e:
        rich.print(
            f"[red]An unexpected error occurred reading '{cut_yaml_path}': {e}[/red]"
        )
        return

    _, original_extension = os.path.splitext(input_video_path)
    if not original_extension:  # Handle cases like filenames without extension
        rich.print(
            f"[yellow]Warning: Could not determine file extension for '{input_video_path}'. Output files might lack an extension.[/yellow]"
        )

    total_scenes = len(scenes_data)
    success_count = 0
    rich.print(f"[blue]Found {total_scenes} scene(s) to process.[/blue]")

    for idx, scene in enumerate(scenes_data):
        if not isinstance(scene, dict):
            rich.print(
                f"[yellow]Warning: Skipping item {idx + 1}/{total_scenes} as it is not a valid scene definition (not a dictionary).[/yellow]"
            )
            continue

        scene_name = scene.get("name")
        start_time_str = scene.get("start")
        end_time_str = scene.get("end")

        if not all([scene_name, start_time_str is not None, end_time_str is not None]):
            rich.print(
                f"[yellow]Warning: Skipping scene {idx + 1}/{total_scenes} (Name: {scene_name}) due to missing 'name', 'start', or 'end' time.[/yellow]"
            )
            continue

        try:
            formatted_start_time = _format_time_for_ffmpeg(start_time_str)
            formatted_end_time = _format_time_for_ffmpeg(end_time_str)
        except ValueError as e:
            rich.print(
                f"[yellow]Warning: Skipping scene '{scene_name}' due to invalid time format: {e}[/yellow]"
            )
            continue

        output_filename = f"{scene_name}{original_extension}"
        output_path = os.path.join(output_folder, output_filename)

        command = [
            "ffmpeg",
            "-i",
            input_video_path,
            "-ss",
            formatted_start_time,
            "-to",
            formatted_end_time,
            "-c",
            "copy",  # Stream copy for efficiency and to avoid re-encoding
            "-y",  # Overwrite output files without asking
            output_path,
        ]

        try:
            rich.print(
                f"[green]Processing scene {idx + 1}/{total_scenes}: '{scene_name}' (from {formatted_start_time} to {formatted_end_time}) -> {output_path}[/green]"
            )
            # Using capture_output=True to get stderr/stdout in case of an error for better reporting
            process = subprocess.run(
                command, capture_output=True, text=True, encoding="utf-8"
            )

            if process.returncode == 0:
                rich.print(f"Successfully extracted '{scene_name}' to '{output_path}'")
                # You can uncomment the following to see ffmpeg's output even on success (often in stderr)
                # if process.stderr:
                #     rich.print(f"[dim]FFmpeg info for '{scene_name}':\n{process.stderr}[/dim]")
                success_count += 1
            else:
                error_message = f"Error extracting scene '{scene_name}'.\n"
                error_message += f"  Command: {' '.join(command)}\n"
                error_message += f"  Return code: {process.returncode}\n"
                if process.stdout:
                    error_message += f"  stdout:\n{process.stdout.strip()}\n"
                if process.stderr:
                    error_message += f"  stderr:\n{process.stderr.strip()}\n"
                rich.print(f"[red]{error_message}[/red]")

        except (
            FileNotFoundError
        ):  # Handles ffmpeg not found if not caught by is_ffmpeg_installed
            rich.print(
                "[red]Error: ffmpeg command not found. Please ensure ffmpeg is installed and in your PATH.[/red]"
            )
            return  # Stop processing if ffmpeg is not found
        except (
            Exception
        ) as e_exec:  # Catch other unexpected errors during subprocess execution
            rich.print(
                f"[red]An unexpected error occurred while processing scene '{scene_name}': {e_exec}[/red]"
            )
            rich.print(f"Command was: {' '.join(command)}")

    rich.print(
        f"[blue]Scene extraction complete. {success_count}/{total_scenes} scenes processed successfully.[/blue]"
    )


@app.command()
def extract_scenes(
    input_video_path: str = typer.Argument(..., help="Path to the source video file."),
    cut_yaml_path: str = typer.Argument(
        ...,
        help="Path to the YAML file defining the scenes to extract (name, start, end).",
    ),
    output_folder: str = typer.Argument(
        ..., help="Directory where the extracted video scenes will be saved."
    ),
):
    """
    Extracts multiple scenes (passages) from a large video file based on a YAML definition
    and saves them as individual files.
    """
    if not is_ffmpeg_installed():  # Assuming is_ffmpeg_installed is available
        rich.print(
            "[red]ffmpeg is not installed or not found in PATH. This command requires ffmpeg.[/red]"
        )
        return

    rich.print(f"[blue]Starting scene extraction from '{input_video_path}'[/blue]")
    rich.print(f"[blue]Using cut definitions from '{cut_yaml_path}'[/blue]")
    rich.print(f"[blue]Outputting to folder: '{output_folder}'[/blue]")

    cut_video_into_scenes(input_video_path, cut_yaml_path, output_folder)
