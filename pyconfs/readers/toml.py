"""Reader for TOML-files


"""

# Standard library imports
import pathlib
from typing import Any, Dict

# Third party imports
import pyplugs
import pytoml

_SUFFIXES = {".toml"}


@pyplugs.register
def read_toml_file(file_path: pathlib.Path) -> Dict[str, Any]:
    """Use pytoml library to read TOML file"""
    with file_path.open(mode="r") as fid:
        cfg = pytoml.load(fid)

    return cfg


@pyplugs.register
def is_format(file_path: pathlib.Path) -> bool:
    """Is the given file of ini-format?"""
    return file_path.suffix in _SUFFIXES
