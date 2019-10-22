"""Reader for YAML-files

"""

# Standard library imports
import pathlib
from typing import Any, Dict

# Third party imports
import pyplugs

# PyConfs imports
from pyconfs._util import delayed_import

# Delayed imports
yaml = delayed_import("yaml")

_SUFFIXES = {".yml", ".yaml"}


@pyplugs.register
def read_toml_file(file_path: pathlib.Path) -> Dict[str, Any]:
    """Use toml library to read TOML file"""
    with file_path.open(mode="r") as fid:
        cfg = yaml.load(fid, Loader=yaml.FullLoader)

    return cfg


@pyplugs.register
def is_format(file_path: pathlib.Path) -> bool:
    """Is the given file of ini-format?"""
    return file_path.suffix in _SUFFIXES
