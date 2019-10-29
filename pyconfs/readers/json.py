"""Reader for JSON-files

"""

# Standard library imports
import json
import pathlib
from typing import Any, Dict

# Third party imports
import pyplugs

_SUFFIXES = {".json"}


@pyplugs.register
def read_json_file(file_path: pathlib.Path) -> Dict[str, Any]:
    """Use json standard library to read JSON file"""
    with file_path.open(mode="r") as fid:
        cfg = json.load(fid)

    return cfg


@pyplugs.register
def is_format(file_path: pathlib.Path) -> bool:
    """Is the given file of json-format?"""
    return file_path.suffix in _SUFFIXES
