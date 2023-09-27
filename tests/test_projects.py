import os

from typer.testing import CliRunner

from flowutils.projects import app
from flowutils.utils import FlowConfig, save_config, load_config

runner = CliRunner()


def test_create_project_dirs(flow_conf: FlowConfig):
    with runner.isolated_filesystem():
        save_config(flow_conf)
        result = runner.invoke(app, ["create"])
        assert result.exit_code == 0

        project_location = flow_conf.project_location
        projects = os.listdir(project_location)
        assert len(projects) == len(flow_conf.project_names)
        subdirs = os.listdir(os.path.join(project_location, projects[0]))
        assert len(subdirs) == len(flow_conf.project_subdirs)


def test_add_project(flow_conf: FlowConfig):
    with runner.isolated_filesystem():
        save_config(flow_conf)
        result = runner.invoke(app, ["add", "project_new"])
        assert result.exit_code == 0
        new_flow_conf = load_config()
        assert "project_new" in new_flow_conf.project_names


def test_list_projects(flow_conf: FlowConfig):
    with runner.isolated_filesystem():
        save_config(flow_conf)

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        assert "project1" in result.output
        assert "Projects" in result.output
