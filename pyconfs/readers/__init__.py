"""Plugins for reading configuration file formats

"""

# Standard library imports
import pathlib
from typing import Any, Dict, Optional

# Third party imports
import pyplugs

# PyConfs imports
from pyconfs import formats

names = pyplugs.names_factory(__package__)
from_str = pyplugs.call_factory(__package__)


def from_file(
    file_path: pathlib.Path,
    file_format: Optional[str] = None,
    encoding: str = "utf-8",
    **reader_args: Any
) -> Dict[str, Any]:
    """Read a configuration from file with the given format

    If the file format is not specified, it is deduced from the file path suffix.
    """
    file_format = (
        formats.guess_format(file_path) if file_format is None else file_format
    )
    return from_str(
        file_format, string=file_path.read_text(encoding=encoding), **reader_args
    )
