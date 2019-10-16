"""A PyConfs Configuration object

The `Configuration` is a collection of `ConfigurationEntry` objects. Entries can
be grouped inside nested Configurations as well.
"""

# Standard library imports
import pathlib
import textwrap
from collections import UserDict
from typing import Any, Dict, List, Optional, Union

# PyConfs imports
from pyconfs import readers


class Configuration(UserDict):
    def __init__(self, name: str = None) -> None:
        """Create an empty configuration"""
        super().__init__()
        self.name = "pyconfs.Configuration" if name is None else name

    @classmethod
    def from_dict(
        cls, entries: Dict[str, Any], name: Optional[str] = None
    ) -> "Configuration":
        """Create a Configuration from a dictionary"""
        cfg = cls(name=name)
        cfg.update_from_dict(entries)
        return cfg

    @classmethod
    def from_file(
        cls,
        file_path: Union[str, pathlib.Path],
        file_format: Optional[str] = None,
        name: Optional[str] = None,
    ) -> "Configuration":
        """Create a Configuration from a file"""
        file_path = pathlib.Path(file_path)
        name = file_path.name if name is None else name

        cfg = cls(name=name)
        cfg.update_from_file(file_path=file_path, file_format=file_format)
        return cfg

    def update_entry(self, key: str, value: Any) -> None:
        """Update one entry in configuration"""
        if isinstance(value, dict):
            self.data[key] = self.from_dict(value, name=key)
        else:
            self.data[key] = value  # ConfigurationEntry(key=key, value=value)

    def update_from_dict(self, entries: Dict[str, Any]) -> None:
        """Update the configuration from a dictionary"""
        for key, value in entries.items():
            self.update_entry(key=key, value=value)

    def update_from_file(
        self, file_path: Union[str, pathlib.Path], file_format: Optional[str] = None
    ) -> None:
        """Update the configuration from a file"""
        file_path = pathlib.Path(file_path)
        file_format = (
            readers.guess_format(file_path) if file_format is None else file_format
        )
        entries = readers.read(file_format, file_path=file_path)
        self.update_from_dict(entries)

    def as_str(self, indent: int = 4, key_width: int = 30) -> str:
        """Represent Configuration as a string"""
        lines = [f"[{self.name}]"]
        for key, value in self.data.items():
            if isinstance(value, self.__class__):
                value_str = value.as_str(indent=indent, key_width=key_width)
                lines.append("\n" + textwrap.indent(value_str, " " * indent))
            else:
                lines.append(f"{key:<{key_width}}= {value!r}")
        return "\n".join(lines)

    def __dir__(self) -> List[str]:
        """Add sections and entries to list of attributes"""
        return list(super().__dir__()) + list(self.data.keys())

    def __getattr__(self, key: str) -> Union["Configuration", "ConfigurationEntry"]:
        return self[key]

    def __repr__(self):
        """Simple representation of a Configuration"""
        return f"{self.__class__.__name__}(name={self.name!r})"

    def __str__(self):
        """Full representation of a Configuration"""
        return self.as_str()
