"""Support simple autodetection of file formats"""

# Standard library imports
import json
import pathlib
from typing import Union

# PyConfs imports
from pyconfs._exceptions import UnknownFormat

# Fall back on backport of importlib.resources
try:
    from importlib import resources
except ImportError:
    import importlib_resources as resources


# Lazily read from formats.json when needed
FORMATS = {}


def guess_format(file_path: Union[str, pathlib.Path]) -> str:
    """Guess the format of a file based on the file suffix"""
    if not FORMATS:
        _read_formats()

    file_path = pathlib.Path(file_path)
    suffix = file_path.suffix
    for format, suffixes in FORMATS.items():
        if suffix in suffixes:
            return format

    raise UnknownFormat(f"Could not guess format of {file_path}")


def _read_formats():
    """Read information about formats from json-file"""
    formats_string = resources.read_text(__package__, "formats.json")
    FORMATS.update(json.loads(formats_string))
