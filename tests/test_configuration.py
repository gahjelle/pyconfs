"""Test Configuration object"""

# Standard library imports
import pathlib

# Third party imports
import pytest

# PyConfs imports
import pyconfs
from pyconfs import _exceptions


@pytest.fixture
def cfg():
    """A basic configuration for testing"""
    return pyconfs.Configuration.from_dict(
        {
            "name": "pyconfs",
            "dependencies": [
                {
                    "name": "python",
                    "url": "https://www.python.org/",
                    "versions": [3.6, 3.7, 3.8, 3.9],
                },
                {"name": "pyplugs", "url": "https://pyplugs.readthedocs.io"},
            ],
            "author": {"firstname": "Geir Arne", "lastname": "Hjelle"},
            "files": {
                "configuration": "{basepath}/pyconfs/configuration.py",
                "toml-reader": "{basepath}/pyconfs/readers/toml.py",
                "test": "{basepath}/tests/test_configuration.py",
            },
            "number": 7,
        },
        name="test_config",
    )


def test_replace(cfg):
    """Test that a variable can be replaced"""
    expected = "/home/tests/test_configuration.py"
    assert cfg.files.replace("test", basepath="/home") == expected


def test_replace_empty(cfg):
    """Test that a variable can be replaced by an empty string"""
    expected = "/tests/test_configuration.py"
    assert cfg.files.replace("test", basepath="") == expected


def test_replace_passthrough(cfg):
    """Test that a variable is passed through if it's not specified"""
    expected = "{basepath}/tests/test_configuration.py"
    assert cfg.files.replace("test") == expected


def test_replace_converter(cfg):
    """Test that a converter can be applied when doing replace"""
    assert isinstance(
        cfg.files.replace("test", basepath="", converter="path"), pathlib.Path
    )


def test_replace_callable_converter(cfg):
    """Test that a callable can be used as a converter when doing replace"""
    assert isinstance(
        cfg.files.replace("test", basepath="", converter=pathlib.Path), pathlib.Path
    )


def test_replace_nonexisting(cfg):
    """Test that replace gives a proper error message when a key is missing"""
    with pytest.raises(KeyError):
        cfg.files.replace("nonexisting")


def test_replace_list_key(cfg):
    """Test that a list can be used to specify nested keys in replace"""
    expected = "{basepath}/tests/test_configuration.py"
    assert cfg.replace(["files", "test"]) == expected


def test_replace_notstring(cfg):
    """Test that replacing a non-string raises a proper error"""
    with pytest.raises(_exceptions.ConversionError):
        cfg.replace("number")
