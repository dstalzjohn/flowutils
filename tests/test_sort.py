import os
import tempfile
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from flowutils.sort import app, sort_folder
from flowutils.utils import SortingRuleConfig, SortFolderConfig, FlowConfig, SortConfig

runner = CliRunner()


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname


def test_sort_folder(temp_dir):
    # Create test files
    open(os.path.join(temp_dir, "document1.pdf"), "w").close()
    open(os.path.join(temp_dir, "image1.jpg"), "w").close()
    open(os.path.join(temp_dir, "other_file.txt"), "w").close()

    rules = [
        SortingRuleConfig(sub_folder_name="PDFs", contain_list=["pdf"]),
        SortingRuleConfig(sub_folder_name="Images", contain_list=["jpg", "png"]),
    ]

    sort_folder(temp_dir, rules)

    assert os.path.exists(os.path.join(temp_dir, "PDFs", "document1.pdf"))
    assert os.path.exists(os.path.join(temp_dir, "Images", "image1.jpg"))
    assert os.path.exists(os.path.join(temp_dir, "other_file.txt"))


@patch("flowutils.sort.load_config")
def test_sort_command(mock_load_config, temp_dir):
    mock_config = FlowConfig(
        sort=SortConfig(
            folder_configs=[
                SortFolderConfig(
                    target_folder=temp_dir,
                    rules=[
                        SortingRuleConfig(sub_folder_name="PDFs", contain_list=["pdf"]),
                        SortingRuleConfig(
                            sub_folder_name="Images", contain_list=["jpg", "png"]
                        ),
                    ],
                )
            ]
        )
    )
    mock_load_config.return_value = mock_config

    # Create test files
    open(os.path.join(temp_dir, "document1.pdf"), "w").close()
    open(os.path.join(temp_dir, "image1.jpg"), "w").close()

    result = runner.invoke(app, ["run"])

    assert result.exit_code == 0
    assert os.path.exists(os.path.join(temp_dir, "PDFs", "document1.pdf"))
    assert os.path.exists(os.path.join(temp_dir, "Images", "image1.jpg"))


@patch("flowutils.sort.load_config")
@patch("flowutils.sort.save_config")
def test_add_rule_command(mock_save_config, mock_load_config):
    mock_config = FlowConfig()
    mock_load_config.return_value = mock_config

    result = runner.invoke(app, ["add-rule", "~/Downloads", "PDFs", "pdf"])

    assert result.exit_code == 0
    assert len(mock_config.sort.folder_configs) == 1
    assert mock_config.sort.folder_configs[0].target_folder == "~/Downloads"
    assert len(mock_config.sort.folder_configs[0].rules) == 1
    assert mock_config.sort.folder_configs[0].rules[0].sub_folder_name == "PDFs"
    assert mock_config.sort.folder_configs[0].rules[0].contain_list == ["pdf"]
    mock_save_config.assert_called_once()


@patch("flowutils.sort.load_config")
def test_list_rules_command(mock_load_config):
    mock_config = FlowConfig(
        sort=SortConfig(
            folder_configs=[
                SortFolderConfig(
                    target_folder="~/Downloads",
                    rules=[
                        SortingRuleConfig(sub_folder_name="PDFs", contain_list=["pdf"]),
                        SortingRuleConfig(
                            sub_folder_name="Images", contain_list=["jpg", "png"]
                        ),
                    ],
                )
            ]
        )
    )
    mock_load_config.return_value = mock_config

    result = runner.invoke(app, ["list"])

    assert result.exit_code == 0
    assert "~/Downloads" in result.output
    assert "PDFs: pdf" in result.output
    assert "Images: jpg, png" in result.output


if __name__ == "__main__":
    pytest.main()
