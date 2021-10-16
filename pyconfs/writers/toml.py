"""Writer for TOML-files

"""

# Standard library imports
from typing import Any, Dict

# Third party imports
import pyplugs

# PyConfs imports
from pyconfs._util import delayed_import
from pyconfs.configuration import Configuration

# Delayed imports
toml = delayed_import("toml")


@pyplugs.register
def as_toml(
    config: Dict[str, Any], pretty_print: bool = False, **toml_args: Any
) -> None:
    """Use toml library to write TOML file"""
    config_with_str_keys = _enforce_str_keys(config)

    if pretty_print:
        return Configuration.from_dict(config_with_str_keys).as_str(**toml_args)
    else:
        return toml.dumps(config_with_str_keys, **toml_args)


def _enforce_str_keys(data: Dict[str, Any]) -> Dict[str, Any]:
    """Changes keys in nested dicts to strings."""
    if isinstance(data, dict):
        return {str(key): _enforce_str_keys(value) for key, value in data.items()}
    return data
