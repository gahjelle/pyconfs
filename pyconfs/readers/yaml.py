"""Reader for YAML-files

"""

# Standard library imports
import pathlib
from typing import Any, Dict

# Third party imports
import pyplugs

# PyConfs imports
from pyconfs._util import delayed_import

# Delayed imports
yaml = delayed_import("yaml")

_SUFFIXES = {".yml", ".yaml"}


@pyplugs.register
def from_yaml(string: str, Loader: Any = None, **yaml_args: Any) -> Dict[str, Any]:
    """Use PyYAML library to read YAML file"""
    Loader = yaml.FullLoader if Loader is None else Loader

    return yaml.load(string, Loader=Loader, **yaml_args)


@pyplugs.register
def is_format(file_path: pathlib.Path) -> bool:
    """Is the given file of yaml-format?"""
    return file_path.suffix in _SUFFIXES
