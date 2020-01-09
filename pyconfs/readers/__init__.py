"""Plugins for reading configuration file formats


"""

# Standard library imports
import pathlib
from typing import Any, Dict, Optional

# Third party imports
import pyplugs

# PyConfs imports
from pyconfs._exceptions import UnknownFormat

names = pyplugs.names_factory(__package__)
from_str = pyplugs.call_factory(__package__)


def from_file(
    file_path: pathlib.Path, file_format: Optional[str] = None, **reader_args: Any
) -> Dict[str, Any]:
    """Read a configuration from file with the given format

    If the file format is not specified, it is deduced from the file path suffix.
    """
    file_format = guess_format(file_path) if file_format is None else file_format
    return from_str(file_format, string=file_path.read_text(), **reader_args)


def guess_format(file_path: pathlib.Path) -> str:
    """Guess the format of a file based on the file suffix"""
    for reader in names():
        if pyplugs.call(__package__, reader, func="is_format", file_path=file_path):
            return reader

    raise UnknownFormat(f"Could not guess format of {file_path}")
