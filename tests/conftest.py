import os

from pytest import fixture

from flowutils.utils import FlowConfig, LinkConfig


@fixture
def config_path():
    return ".flowutils/config.yaml"


@fixture
def configure_env(config_path: str):
    os.environ["FLOW_CONFIG"] = config_path


@fixture
def flow_conf(configure_env) -> FlowConfig:
    link_list = [
        LinkConfig(target="./Projects/project1/subdir1", name="project1"),
    ]
    flow_config = FlowConfig(
        link_location="./Links",
        project_location="./Projects",
        project_names=["project1", "project2", "project3"],
        project_subdirs=["subdir1", "subdir2"],
        links=link_list,
    )
    return flow_config
