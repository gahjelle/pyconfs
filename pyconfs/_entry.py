"""A PyConfs ConfigurationEntry object

The `ConfigurationEntry` is a mapping from a key to a value.
"""

# Standard library imports
from dataclasses import dataclass
from typing import Any


@dataclass
class ConfigurationEntry:

    key: str
    value: Any

    def __str__(self):
        return str(self.value)
