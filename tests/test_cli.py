import os
from os.path import abspath

import yaml
from typer.testing import CliRunner
from flowutils.cli import app, load_config, save_config, FlowConfig

runner = CliRunner()


def test_init(config_path: str):
    with runner.isolated_filesystem():
        os.makedirs("./CustomProjects/Project1")
        result = runner.invoke(
            app,
            ["init", "--link-location", "./CustomLinks", "--project-location", "./CustomProjects", "--capture"],
            input="y\n"
        )

        assert result.exit_code == 0
        assert result.output.strip().endswith(f"Config file created at: {config_path}")

        config = load_config()
        assert config.link_location == "./CustomLinks"
        assert config.project_location == "./CustomProjects"
        assert isinstance(config.project_names, list)
        assert len(config.project_names) == 1


def test_create_project_dirs(config_path: str):
    with runner.isolated_filesystem():
        config_path = os.path.expanduser(config_path)
        os.makedirs(os.path.dirname(config_path), exist_ok=True)

        config = FlowConfig(link_location="./Links", project_location="./Projects",
                            project_names=["project1", "project2", "project3"],
                            project_subdirs=["subdir1", "subdir2"], links=[])

        save_config(config)

        result = runner.invoke(app, ["create-project-dirs"])

        assert result.exit_code == 0

        project_location = os.path.expanduser("./Projects")
        project_names = ["project1", "project2", "project3"]
        project_subdirs = ["subdir1", "subdir2"]

        for name in project_names:
            for subdir in project_subdirs:
                assert os.path.exists(os.path.join(project_location, name, subdir))


def test_add_project(config_path: str):
    with runner.isolated_filesystem():
        config_path = os.path.expanduser(config_path)
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        config = FlowConfig(link_location="./Links", project_location="./Projects",
                            project_names=["project1", "project2"],
                            project_subdirs=["subdir1", "subdir2"], links=[])

        save_config(config)

        result = runner.invoke(app, ["add-project", "project3"])

        assert result.exit_code == 0

        updated_config = load_config()
        assert "project3" in updated_config.project_names


def test_create_links(config_path: str):
    with runner.isolated_filesystem():
        os.makedirs("./Target1")
        config_path = os.path.expanduser(config_path)
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, "w") as f:
            config = {
                "link_location": "./Links",
                "project_location": "./Projects",
                "project_names": [],
                "project_subdirs": [],
                "links": [
                    {"target": abspath("./Target1"), "name": "link1"},
                ]
            }
            yaml.dump(config, f)

        result = runner.invoke(app, ["create-links"])

        assert result.exit_code == 0

        link_location = os.path.expanduser("./Links")

        assert os.path.exists(os.path.join(link_location, "link1"))


def test_add_link(config_path: str):
    with runner.isolated_filesystem():
        config_path = os.path.expanduser(config_path)
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, "w") as f:
            config = {
                "link_location": "./Links",
                "project_location": "./Projects",
                "project_names": [],
                "project_subdirs": [],
                "links": []
            }
            yaml.dump(config, f)

        result = runner.invoke(app, ["add-link", "/path/to/target", "linkname"])

        assert result.exit_code == 0

        with open(os.path.expanduser(config_path)) as f:
            updated_config = yaml.safe_load(f)
            assert len(updated_config["links"]) == 1
            assert updated_config["links"][0]["target"] == "/path/to/target"
            assert updated_config["links"][0]["name"] == "linkname"
