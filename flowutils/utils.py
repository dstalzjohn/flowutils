import os
from os.path import expanduser

import yaml
from pydantic import BaseModel


class LinkConfig(BaseModel):
    """Link config model."""

    target: str
    name: str


class GitRepoConfig(BaseModel):
    """Git repo config model."""

    url: str
    file_location: str


class FlowConfig(BaseModel):
    """Flow config model."""

    link_location: str = "~/Links"
    project_location: str = "~/Projects"
    project_names: list[str] = []
    project_subdirs: list[str] = []
    links: list[LinkConfig] = []
    git_repos: list[GitRepoConfig] = []

    def get_project_location(self) -> str:
        return expanduser(self.project_location)

    def get_link_location(self) -> str:
        return expanduser(self.link_location)


def get_config_path():
    """Get the path to the config file. If the FLOW_CONFIG environment variable is set, use that."""
    flow_config = os.environ.get("FLOW_CONFIG", "~/.flowutils/config.yaml")
    return os.path.expanduser(flow_config)


def load_config() -> FlowConfig:
    """Load the config file."""
    config_path = get_config_path()
    with open(config_path, "r") as f:
        dict_conf = yaml.safe_load(f)
    return FlowConfig(**dict_conf)


def save_config(config: FlowConfig):
    """Save the config file."""
    config_path = get_config_path()
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, "w") as f:
        yaml.dump(config.model_dump(), f)
