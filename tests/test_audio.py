from os.path import isfile

from pydub import AudioSegment
from typer.testing import CliRunner
from flowutils import audio
from flowutils.audio import is_ffmpeg_installed

runner = CliRunner()


def test_to_m4a():
    assert is_ffmpeg_installed()
    with runner.isolated_filesystem():
        # Create a silent audio segment with a duration of 5 seconds
        silence = AudioSegment.silent(duration=5000)

        # Export the silent segment as an MP3 file
        silence.export("silence.mp3", format="mp3")

        # Convert the MP3 file to an M4A file
        result = runner.invoke(audio.app, ["to-m4a", "silence.mp3"])

        assert result.exit_code == 0
        assert isfile("silence.m4a")


def test_audio():
    assert is_ffmpeg_installed()
    with runner.isolated_filesystem():
        # Create a silent audio segment with a duration of 5 seconds
        silence = AudioSegment.silent(duration=5000)

        # Export the silent segment as an MP3 file
        silence.export("silence.mp3", format="mp3")

        # Convert the MP3 file to an M4A file
        result = runner.invoke(audio.app, ["info", "silence.mp3"])

        assert result.exit_code == 0
        assert "5" in result.output
        assert "mp3" in result.output
