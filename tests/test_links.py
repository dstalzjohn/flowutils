import os

from typer.testing import CliRunner

from flowutils.links import app
from flowutils.utils import save_config, FlowConfig, load_config

runner = CliRunner()


def test_create_links(flow_conf):
    with runner.isolated_filesystem():
        save_config(flow_conf)
        result = runner.invoke(app, ["create"])
        assert result.exit_code == 0

        link_location = os.path.expanduser("./Links")
        links = os.listdir(link_location)
        assert len(links) == len(flow_conf.links)


def test_add_link(flow_conf: FlowConfig):
    with runner.isolated_filesystem():
        save_config(flow_conf)

        result = runner.invoke(app, ["add", "/path/to/target", "linkname"])

        assert result.exit_code == 0

        new_flow_conf = load_config()
        assert len(flow_conf.links) + 1 == len(new_flow_conf.links)


def test_list_links(flow_conf: FlowConfig):
    with runner.isolated_filesystem():
        save_config(flow_conf)

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        assert "project1" in result.output
        assert "Links:" in result.output
        assert "->" in result.output
