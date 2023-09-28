import subprocess
from typing import Optional

import rich
import typer
from pydub import AudioSegment

app = typer.Typer()


@app.command()
def toipod(mp3_file_path: str =
           typer.Argument(help="Location path of the mp3 input file"),
           m4a_file_path: Optional[str] = typer.Argument(None, help="Location path of the m4a file")):
    """Convert mp3 file to m4a file."""
    if not is_ffmpeg_installed():
        rich.print("[red]ffmpeg is not installed.")
        return
    if m4a_file_path is None:
        m4a_file_path = mp3_file_path.replace(".mp3", ".m4a")
    convert_mp3_to_m4a(mp3_file_path, m4a_file_path)
    rich.print(f"[blue]M4A file created at: {m4a_file_path}")


@app.command()
def info(file_path: str = typer.Argument(help="Location path of the sound input file")):
    """Get info about an mp3 file."""
    if not is_ffmpeg_installed():
        rich.print("[red]ffmpeg is not installed.")
        return
    sound = AudioSegment.from_file(file_path)
    # Get the file type of the audio file
    rich.print(f"[blue]File duration: {sound.duration_seconds:03f} s")


def is_ffmpeg_installed():
    """Check if ffmpeg is installed."""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def convert_mp3_to_m4a(mp3_file_path, m4a_file_path):
    """Convert mp3 file to m4a file."""
    mp3_audio = AudioSegment.from_mp3(mp3_file_path)
    mp3_audio.export(m4a_file_path, format='ipod')