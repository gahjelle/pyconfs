"""Reader for YAML-files

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
def from_yaml(string: str, Loader: Any = None, **yaml_args: Any) -> Dict[str, Any]:
    """Use PyYAML library to read YAML file"""
    Loader = yaml.FullLoader if Loader is None else Loader

    try:
        return yaml.load(string, Loader=Loader, **yaml_args)
    except yaml.composer.ComposerError:
        return next(yaml.load_all(string, Loader=Loader, **yaml_args))
