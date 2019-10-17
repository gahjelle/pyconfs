"""A PyConfs Configuration object

The `Configuration` is a collection of `ConfigurationEntry` objects. Entries can
be grouped inside nested Configurations as well.
"""

# Standard library imports
import functools
import pathlib
import textwrap
from collections import UserDict
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Set, Tuple, Union

# PyConfs imports
from pyconfs import converters, exceptions, readers


def _dispatch_to(converter):
    """Decorator for dispatching methods to converter functions"""

    def _decorator_dispatch_to(func):
        @functools.wraps(func)
        def _wrapper_dispatch_to(self, key: str, **options):
            return converter(value=func(self, key), **options)

        return _wrapper_dispatch_to

    return _decorator_dispatch_to


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
            self.data[key] = value

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

    #
    # Add converters used to convert entries to certain types
    #
    def _get_value(self, key: str) -> Any:
        """Get single value, raise an error if key points to a Configuration object"""
        value = self.data[key]
        if isinstance(value, self.__class__):
            raise exceptions.EntryError(f"{self.name}.{key!r} is a Configuration")

        return value

    @_dispatch_to(converters.to_str)
    def to_str(self, key: str) -> str:
        """Convert entry to string"""
        return self._get_value(key)

    @_dispatch_to(converters.to_int)
    def to_int(self, key: str) -> int:
        """Convert entry to integer number"""
        return self._get_value(key)

    @_dispatch_to(converters.to_float)
    def to_float(self, key: str) -> float:
        """Convert entry to a floating point number"""
        return self._get_value(key)

    @_dispatch_to(converters.to_bool)
    def to_bool(self, key: str) -> bool:
        """Convert entry to a boolean"""
        return self._get_value(key)

    @_dispatch_to(converters.to_date)
    def to_date(self, key: str) -> date:
        """Convert entry to a date"""
        return self._get_value(key)

    @_dispatch_to(converters.to_datetime)
    def to_datetime(self, key: str) -> datetime:
        """Convert entry to a datetime"""
        return self._get_value(key)

    @_dispatch_to(converters.to_path)
    def to_path(self, key: str) -> pathlib.Path:
        """Convert entry to a path"""
        return self._get_value(key)

    @_dispatch_to(converters.to_list)
    def to_list(self, key: str) -> List[Any]:
        """Convert entry to a list"""
        return self._get_value(key)

    @_dispatch_to(converters.to_dict)
    def to_dict(self, key: str) -> Dict[str, Any]:
        """Convert entry to a dictionary"""
        return self._get_value(key)

    @_dispatch_to(converters.to_set)
    def to_set(self, key: str) -> Set[Any]:
        """Convert entry to a set"""
        return self._get_value(key)

    @_dispatch_to(converters.to_tuple)
    def to_tuple(self, key: str, **options: Any) -> Tuple[Any, ...]:
        """Convert entry to a tuple"""
        return self._get_value(key)

    #
    # Dunder methods
    #
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
