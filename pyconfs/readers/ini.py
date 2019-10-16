"""Reader for ini-files based on ConfigParser


"""

# Standard library imports
import pathlib
from configparser import ConfigParser
from typing import Any, Dict

# Third party imports
import pyplugs

_SUFFIXES = {".ini", ".conf"}


@pyplugs.register
def read_ini_file(file_path: pathlib.Path) -> Dict[str, Any]:
    """Use ConfigParser to read an ini-file"""
    cfg = ConfigParser()
    files = cfg.read(file_path)
    if not files:
        raise FileNotFoundError(f"{file_path} could not be opened by ConfigParser")

    # Ini-files organize into sections with key, value pairs
    entries = {
        sn: {k: v for k, v in s.items()} for sn, s in cfg.items() if not sn == "DEFAULT"
    }

    # Ini-files by default does not support type information (everything is a string)
    # Add possibility to specify types using a special :-syntax

    return entries


@pyplugs.register
def is_format(file_path: pathlib.Path) -> bool:
    """Is the given file of ini-format?"""
    return file_path.suffix in _SUFFIXES
