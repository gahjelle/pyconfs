"""Reader for TOML-files

"""

# Standard library imports
import pathlib
from typing import Any, Dict

# Third party imports
import pyplugs

# PyConfs imports
from pyconfs._util import delayed_import

# Delayed imports
toml = delayed_import("toml")

_SUFFIXES = {".toml"}


@pyplugs.register
def read_toml_file(file_path: pathlib.Path) -> Dict[str, Any]:
    """Use toml library to read TOML file"""
    with file_path.open(mode="r") as fid:
        cfg = toml.load(fid)

    return cfg


@pyplugs.register
def is_format(file_path: pathlib.Path) -> bool:
    """Is the given file of toml-format?"""
    return file_path.suffix in _SUFFIXES
