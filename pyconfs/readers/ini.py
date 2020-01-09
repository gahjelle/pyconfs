"""Reader for ini-files based on ConfigParser

"""

# Standard library imports
from configparser import ConfigParser
from typing import Any, Dict

# Third party imports
import pyplugs

# PyConfs imports
from pyconfs import _converters

# Support type information in ini-files
_TYPE_SUFFIX = ":type"


@pyplugs.register
def from_ini(string: str, **ini_args: Any) -> Dict[str, Any]:
    """Use ConfigParser to read an ini-file"""
    cfg = ConfigParser(delimiters=("=",), **ini_args)
    cfg.read_string(string)

    # Convert to nested dictionary and interpret given types
    return _convert_types(
        {
            name: {k: v for k, v in section.items()}
            for name, section in cfg.items()
            if not name == "DEFAULT"
        }
    )


def _convert_types(entries: Dict[str, str]) -> Dict[str, Any]:
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
        entries[master] = _converters.convert(f"to_{value}", value=entries[master])
        del entries[key]

    return entries
