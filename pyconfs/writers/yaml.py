"""Writer for YAML-files

"""

# Standard library imports
from typing import Any, Dict

# Third party imports
import pyplugs

# PyConfs imports
from pyconfs._util import delayed_import

# Delayed imports
yaml = delayed_import("yaml")


@pyplugs.register
def as_yaml(config: Dict[str, Any], **yaml_args: Any) -> str:
    """Use PyYAML library to write YAML file"""
    return yaml.dump(config, **yaml_args)
