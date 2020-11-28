"""Test reading of configuration files"""

# Standard library imports
import pathlib

# Third party imports
import pytest

# PyConfs imports
from pyconfs import Configuration


@pytest.fixture
def sample_dir():
    """Directory that contains sample files"""
    return pathlib.Path(__file__).parent / "files"


def test_read_ini(sample_dir):
    """Test that reading an INI file succeeds"""
    Configuration.from_file(sample_dir / "sample.ini")


def test_read_ini_sources(sample_dir):
    """Test that source is set correctly when reading an INI file"""
    cfg_path = sample_dir / "sample.ini"
    cfg = Configuration.from_file(cfg_path)

    assert cfg.sources == {f"{cfg_path} (INI reader)"}


def test_read_json(sample_dir):
    """Test that reading an JSON file succeeds"""
    Configuration.from_file(sample_dir / "sample.json")


def test_read_json_sources(sample_dir):
    """Test that source is set correctly when reading a JSON file"""
    cfg_path = sample_dir / "sample.json"
    cfg = Configuration.from_file(cfg_path)

    assert cfg.sources == {f"{cfg_path} (JSON reader)"}


def test_read_toml(sample_dir):
    """Test that reading a TOML file succeeds"""
    Configuration.from_file(sample_dir / "sample.toml")


def test_read_toml_sources(sample_dir):
    """Test that source is set correctly when reading a TOML file"""
    cfg_path = sample_dir / "sample.toml"
    cfg = Configuration.from_file(cfg_path)

    assert cfg.sources == {f"{cfg_path} (TOML reader)"}


def test_read_yaml(sample_dir):
    """Test that reading a YAML file succeeds"""
    Configuration.from_file(sample_dir / "sample.yaml")


def test_read_yaml_sources(sample_dir):
    """Test that source is set correctly when reading a YAML file"""
    cfg_path = sample_dir / "sample.yaml"
    cfg = Configuration.from_file(cfg_path)

    assert cfg.sources == {f"{cfg_path} (YAML reader)"}
