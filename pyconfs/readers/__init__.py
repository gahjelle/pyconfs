"""Plugins for reading configuration file formats


"""

# Standard library imports
import pathlib

# Third party imports
import pyplugs

# PyConfs imports
from pyconfs.exceptions import UnknownFormat

names = pyplugs.names_factory(__package__)
read = pyplugs.call_factory(__package__)


def guess_format(file_path: pathlib.Path) -> str:
    """Guess the format of a file based on the file suffix"""
    for reader in names():
        if pyplugs.call(__package__, reader, func="is_format", file_path=file_path):
            return reader

    raise UnknownFormat(f"Could not guess format of {file_path}")
