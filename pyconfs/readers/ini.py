"""Reader for ini-files based on ConfigParser


"""

# Standard library imports
import pathlib
from configparser import ConfigParser
from typing import Any, Dict

# Third party imports
import pyplugs

# PyConfs imports
from pyconfs import converters

_SUFFIXES = {".ini", ".conf"}
_TYPE_SUFFIX = ":type"


@pyplugs.register
def read_ini_file(file_path: pathlib.Path) -> Dict[str, Any]:
    """Use ConfigParser to read an ini-file"""
    cfg = ConfigParser(delimiters=("=",))
    files = cfg.read(file_path)
    if not files:
        raise FileNotFoundError(f"{file_path} could not be opened by ConfigParser")

    # Ini-files organize into sections with key, value pairs
    return _convert_types(
        {
            name: {k: v for k, v in section.items()}
            for name, section in cfg.items()
            if not name == "DEFAULT"
        }
    )


def _convert_types(entries):
    """Convert values inside entries dictionary based on type information

    Ini-files by default does not support type information (everything is a
    string) Add possibility to specify types using a special :-syntax (see
    _TYPE_SUFFIX)
    """
    for key, value in entries.copy().items():
        # Recursively convert types in subdictionaries
        if isinstance(value, dict):
            _convert_types(value)
            continue

        # Find type information
        if not key.endswith(_TYPE_SUFFIX):
            continue
        master = key.partition(_TYPE_SUFFIX)[0]
        if master not in entries:
            continue

        # Convert entry to the given type
        entries[master] = converters.convert(f"to_{value}", value=entries[master])
        del entries[key]


@pyplugs.register
def is_format(file_path: pathlib.Path) -> bool:
    """Is the given file of ini-format?"""
    return file_path.suffix in _SUFFIXES
