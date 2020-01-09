"""Reader for TOML-files

"""

# Standard library imports
from typing import Any, Dict

# Third party imports
import pyplugs

# PyConfs imports
from pyconfs._util import delayed_import

# Delayed imports
toml = delayed_import("toml")


@pyplugs.register
def from_toml(string: str, **toml_args: Any) -> Dict[str, Any]:
    """Use toml library to read TOML file"""
    return toml.loads(string, **toml_args)
