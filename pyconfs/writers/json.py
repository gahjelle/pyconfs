"""Writer for JSON-files

"""

# Standard library imports
import json
from typing import Any, Dict

# Third party imports
import pyplugs


@pyplugs.register
def as_json(config: Dict[str, Any], **json_args: Any) -> None:
    """Use json standard library to write JSON file"""
    return json.dumps(config, **json_args)
