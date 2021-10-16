"""Common fixtures for all tests"""

# Third party imports
import pytest

# PyConfs imports
import pyconfs


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
                    "versions": [3.6, 3.7, 3.8, 3.9, 3.10],
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
