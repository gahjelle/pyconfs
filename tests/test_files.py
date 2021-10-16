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


@pytest.fixture
def cfg_with_int_key():
    """Configuration with a key that is an integer"""
    return Configuration.from_dict(
        {
            "answer": {42: "Life, the Universe, and Everything"},
            "long_answer": {
                "parts": {
                    1: "The Answer to the Ultimate Question of",
                    2: "Life, the Universe, and Everything",
                },
            },
        }
    )


def test_read_ini(sample_dir):
    """Test that reading an INI file succeeds"""
    Configuration.from_file(sample_dir / "sample.ini")


def test_read_ini_sources(sample_dir):
    """Test that source is set correctly when reading an INI file"""
    cfg_path = sample_dir / "sample.ini"
    cfg = Configuration.from_file(cfg_path)

    assert cfg.sources == {f"{cfg_path} (INI reader)"}


@pytest.mark.skip("INI does not yet support advanced reading")
def test_ini_roundtrip(cfg):
    """Test that a configuration can be recovered after being stored as INI"""
    roundtripped = Configuration.from_str(cfg.as_str(format="ini"), format="ini")

    assert roundtripped.as_dict() == cfg.as_dict()


def test_ini_handle_int_key_gracefully(cfg_with_int_key):
    """Test that INI format handles int keys gracefully"""
    roundtripped = Configuration.from_str(
        cfg_with_int_key.as_str(format="ini"), format="ini"
    )

    # INI converts integer keys to strings
    assert roundtripped.answer.entry_keys == ["42"]

    # Subsections are not properly supported by INI reader
    # assert roundtripped.long_answer.parts.entry_keys == ["1", "2"]


def test_read_json(sample_dir):
    """Test that reading an JSON file succeeds"""
    Configuration.from_file(sample_dir / "sample.json")


def test_read_json_sources(sample_dir):
    """Test that source is set correctly when reading a JSON file"""
    cfg_path = sample_dir / "sample.json"
    cfg = Configuration.from_file(cfg_path)

    assert cfg.sources == {f"{cfg_path} (JSON reader)"}


def test_json_roundtrip(cfg):
    """Test that a configuration can be recovered after being stored as JSON"""
    roundtripped = Configuration.from_str(cfg.as_str(format="json"), format="json")

    assert roundtripped.as_dict() == cfg.as_dict()


def test_json_handle_int_key_gracefully(cfg_with_int_key):
    """Test that JSON format handles int keys gracefully"""
    roundtripped = Configuration.from_str(
        cfg_with_int_key.as_str(format="json"), format="json"
    )

    # JSON converts integer keys to strings
    assert roundtripped.answer.entry_keys == ["42"]
    assert roundtripped.long_answer.parts.entry_keys == ["1", "2"]


def test_read_toml(sample_dir):
    """Test that reading a TOML file succeeds"""
    Configuration.from_file(sample_dir / "sample.toml")


def test_read_toml_sources(sample_dir):
    """Test that source is set correctly when reading a TOML file"""
    cfg_path = sample_dir / "sample.toml"
    cfg = Configuration.from_file(cfg_path)

    assert cfg.sources == {f"{cfg_path} (TOML reader)"}


def test_toml_roundtrip(cfg):
    """Test that a configuration can be recovered after being stored as TOML"""
    roundtripped = Configuration.from_str(cfg.as_str(format="toml"), format="toml")

    assert roundtripped.as_dict() == cfg.as_dict()


def test_toml_handle_int_key_gracefully(cfg_with_int_key):
    """Test that TOML format handles int keys gracefully"""
    roundtripped = Configuration.from_str(
        cfg_with_int_key.as_str(format="toml"), format="toml"
    )

    # TOML converts integer keys to strings
    assert roundtripped.answer.entry_keys == ["42"]
    assert roundtripped.long_answer.parts.entry_keys == ["1", "2"]


def test_read_yaml(sample_dir):
    """Test that reading a YAML file succeeds"""
    Configuration.from_file(sample_dir / "sample.yaml")


def test_read_yaml_sources(sample_dir):
    """Test that source is set correctly when reading a YAML file"""
    cfg_path = sample_dir / "sample.yaml"
    cfg = Configuration.from_file(cfg_path)

    assert cfg.sources == {f"{cfg_path} (YAML reader)"}


def test_yaml_roundtrip(cfg):
    """Test that a configuration can be recovered after being stored as YAML"""
    roundtripped = Configuration.from_str(cfg.as_str(format="yaml"), format="yaml")

    assert roundtripped.as_dict() == cfg.as_dict()


def test_yaml_handle_int_key_gracefully(cfg_with_int_key):
    """Test that YAML format handles int keys gracefully"""
    roundtripped = Configuration.from_str(
        cfg_with_int_key.as_str(format="yaml"), format="yaml"
    )

    # YAML supports integer keys
    assert roundtripped.as_dict() == cfg_with_int_key.as_dict()
