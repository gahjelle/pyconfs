"""Reader for JSON-files

"""

# Standard library imports
import json
from typing import Any, Dict

# Third party imports
import pyplugs


@pyplugs.register
def from_json(string: str, **json_args: Any) -> Dict[str, Any]:
    """Use json standard library to read JSON"""
    return json.loads(string, **json_args)
