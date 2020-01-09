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
def from_toml(string: str, **toml_args: Any) -> Dict[str, Any]:
    """Use toml library to read TOML file"""
    return toml.loads(string, **toml_args)


@pyplugs.register
def is_format(file_path: pathlib.Path) -> bool:
    """Is the given file of toml-format?"""
    return file_path.suffix in _SUFFIXES
