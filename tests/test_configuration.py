"""Test Configuration object"""

# Standard library imports
import pathlib

# Third party imports
import pytest

# PyConfs imports
from pyconfs import _exceptions
from pyconfs.configuration import ConfigurationList


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
        cfg.files.replace("test", basepath="", converter=pathlib.Path),
        pathlib.Path,
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
        cfg.stuff.replace("number")


def test_config_is_not_list(cfg):
    """Test that Configuration does not identify as a list"""
    assert not cfg.is_list


def test_config_is_list(cfg):
    """Test that ConfigurationList identifies as a list"""
    assert cfg.dependencies.is_list


def test_section_keeps_variables(cfg):
    """Test that variables are preserved in configuration sections"""
    assert cfg.files.vars == cfg.vars


def test_configlist_keeps_variables(cfg):
    """Test that variables are preserved in ConfigurationList objects"""
    assert cfg.dependencies.vars == cfg.vars


def test_configlist_elements_keep_variables(cfg):
    """Test that variables are preserved in ConfigurationList elements"""
    assert cfg.dependencies[0].vars == cfg.vars


def test_plain_list_is_python_list(cfg):
    """Test that plain lists are represented as Python lists"""
    assert isinstance(cfg.stuff["400 m hurdles"], list)


def test_nested_list_is_configlist(cfg):
    """Test that nested lists are represented as ConfigurationList objects"""
    assert isinstance(cfg.dependencies, ConfigurationList)
