"""Test reading of configuration files"""

# Standard library imports
import pathlib
from typing import List, NamedTuple

# Third party imports
import pytest

# PyConfs imports
from pyconfs import Configuration


@pytest.fixture
def sample_dir():
    """Directory that contains sample files"""
    return pathlib.Path(__file__).parent / "files"


@pytest.fixture
def sample_cfg(sample_dir):
    """Sample configuration"""
    return Configuration.from_file(sample_dir / "sample.toml")


def test_named_tuple(sample_cfg):
    """Test that configuration can be converted to a named tuple"""
    author = sample_cfg.author.as_named_tuple()
    assert author.firstname == sample_cfg.author.firstname


def test_named_tuple_with_validation(sample_cfg):
    """Test that configuration can be validated with a named tuple"""

    class Author(NamedTuple):
        """Author template"""

        firstname: str
        lastname: str

    author = sample_cfg.author.as_named_tuple(Author)
    assert author.firstname == sample_cfg.author.firstname


def test_named_tuple_with_default(sample_cfg):
    """Test that named tuple can use default values"""

    class Author(NamedTuple):
        """Author template"""

        firstname: str
        lastname: str
        country: str = "Norway"

    author = sample_cfg.author.as_named_tuple(Author)
    assert author.country == "Norway"


def test_named_tuple_with_missing_value(sample_cfg):
    """Test that named tuple raises error on missing values"""

    class Author(NamedTuple):
        """Author template"""

        firstname: str
        lastname: str
        country: str

    with pytest.raises(TypeError) as err:
        sample_cfg.author.as_named_tuple(Author)

    expected = (
        "Configuration 'author' missing 1 required positional argument: 'country' "
        f"({', '.join(sample_cfg.sources)})"
    )
    assert str(err.value) == expected


def test_named_tuple_with_extra_value(sample_cfg):
    """Test that named tuple raises error on extra values"""

    class Author(NamedTuple):
        """Author template"""

        firstname: str

    with pytest.raises(TypeError) as err:
        sample_cfg.author.as_named_tuple(Author)

    expected = (
        "Configuration 'author' got an unexpected keyword argument 'lastname' "
        f"({', '.join(sample_cfg.sources)})"
    )
    assert str(err.value) == expected


def test_named_tuple_with_wrong_type(sample_cfg):
    """Test that named tuple raises error on wrong types"""

    class Author(NamedTuple):
        """Author template"""

        firstname: str
        lastname: int

    with pytest.raises(TypeError) as err:
        sample_cfg.author.as_named_tuple(Author)

    expected = (
        "Configuration author got 'str' type for field lastname. "
        f"Author requires 'int' ({', '.join(sample_cfg.sources)})"
    )
    assert str(err.value) == expected


def test_named_tuple_with_wrong_template(sample_cfg):
    """Test behavior on other mappings"""

    author = sample_cfg.author.as_named_tuple(dict)

    expected = {"firstname": "Geir Arne", "lastname": "Hjelle"}
    assert author == expected


def test_named_tuple_with_generics(sample_cfg):
    """Test that named tuple handles unsupported generics gracefully"""

    class Author(NamedTuple):
        """Author template"""

        firstname: str
        lastname: List[str]

    author = sample_cfg.author.as_named_tuple(Author)
    assert author.lastname == "Hjelle"
