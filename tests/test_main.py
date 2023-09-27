import os

from typer.testing import CliRunner
from flowutils.main import app
from flowutils.utils import load_config

runner = CliRunner()


def test_init(configure_env, config_path: str):
    with runner.isolated_filesystem():
        os.makedirs("./CustomProjects/Project1")
        result = runner.invoke(
            app,
            [
                "init",
                "--link-location",
                "./CustomLinks",
                "--project-location",
                "./CustomProjects",
                "--capture",
            ],
            input="y\n",
        )

        assert result.exit_code == 0
        assert result.output.strip().endswith(f"Config file created at: {config_path}")

        config = load_config()
        assert config.link_location == "./CustomLinks"
        assert config.project_location == "./CustomProjects"
        assert isinstance(config.project_names, list)
        assert len(config.project_names) == 1
