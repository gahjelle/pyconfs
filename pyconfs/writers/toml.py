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
    if pretty_print:
        return Configuration.from_dict(config).as_str(**toml_args)
    else:
        return toml.dumps(config, **toml_args)
