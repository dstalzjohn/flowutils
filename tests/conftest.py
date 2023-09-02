import os

from pytest import fixture


@fixture
def config_path():
    return ".flowutils/config.yaml"


def pytest_configure(config):
    os.environ["FLOW_CONFIG"] = ".flowutils/config.yaml"
