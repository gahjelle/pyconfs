"""Writer for JSON-files

"""

# Standard library imports
import json
import pathlib
from typing import Any, Dict

# Third party imports
import pyplugs

_SUFFIXES = {".json"}


@pyplugs.register
def as_json(config: Dict[str, Any], **json_args: Any) -> None:
    """Use json standard library to write JSON file"""
    return json.dumps(config, **json_args)


@pyplugs.register
def is_format(file_path: pathlib.Path) -> bool:
    """Is the given file of json-format?"""
    return file_path.suffix in _SUFFIXES
