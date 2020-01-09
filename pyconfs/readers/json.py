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
def from_json(string: str, **json_args: Any) -> Dict[str, Any]:
    """Use json standard library to read JSON"""
    return json.loads(string, **json_args)


@pyplugs.register
def is_format(file_path: pathlib.Path) -> bool:
    """Is the given file of json-format?"""
    return file_path.suffix in _SUFFIXES
