"""Writer for TOML-files

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
def as_toml(config: Dict[str, Any], **toml_args: Any) -> None:
    """Use toml library to write TOML file"""
    return toml.dumps(config, **toml_args)


@pyplugs.register
def is_format(file_path: pathlib.Path) -> bool:
    """Is the given file of toml-format?"""
    return file_path.suffix in _SUFFIXES
