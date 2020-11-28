"""Test reading of configuration files"""

# Standard library imports
import pathlib

# Third party imports
import pytest

# PyConfs imports
from pyconfs import Configuration


@pytest.fixture
def sample_path():
    """Path to sample files"""
    return pathlib.Path(__file__).parent / "files"


def test_read_ini(sample_path):
    """Test that reading an INI file succeeds"""
    Configuration.from_file(sample_path / "sample.ini")


def test_read_json(sample_path):
    """Test that reading an JSON file succeeds"""
    Configuration.from_file(sample_path / "sample.json")


def test_read_toml(sample_path):
    """Test that reading an TOML file succeeds"""
    Configuration.from_file(sample_path / "sample.toml")


def test_read_yaml(sample_path):
    """Test that reading an YAML file succeeds"""
    Configuration.from_file(sample_path / "sample.yaml")
