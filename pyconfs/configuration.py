"""A PyConfs Configuration object

The `Configuration` is a collection of `ConfigurationEntry` objects. Entries can
be grouped inside nested Configurations as well.
"""

# Standard library imports
import functools
import os
import pathlib
import re
import textwrap
from collections import UserDict
from datetime import date, datetime
from typing import Any, Callable, Dict, List, Optional, Sequence, Set, Tuple, Union

# PyConfs imports
from pyconfs import _converters, _exceptions, readers


def _dispatch_to(converter):
    """Decorator for dispatching methods to converter functions"""

    def _decorator_dispatch_to(func):
        @functools.wraps(func)
        def _wrapper_dispatch_to(self, key: str, **options):
            return converter(value=func(self, key), **options)

        return _wrapper_dispatch_to

    return _decorator_dispatch_to


class Configuration(UserDict):
    def __init__(
        self, name: Optional[str] = None, _vars: Optional[Dict[str, str]] = None
    ) -> None:
        """Create an empty configuration"""
        super().__init__()
        self.name = "pyconfs.Configuration" if name is None else name
        self.vars = {} if _vars is None else _vars
        self._source = {}

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

    def update_entry(self, key: str, value: Any, source: str = "") -> None:
        """Update one entry in configuration"""
        if isinstance(value, dict):
            self.data.setdefault(key, self.__class__(name=key, _vars=self.vars))
            self.data[key].update_from_dict(value, source=source)
        else:
            self.data[key] = value
            self._source[key] = source

    def update_from_dict(self, entries: Dict[str, Any], source: str = "") -> None:
        """Update the configuration from a dictionary"""
        for key, value in entries.items():
            self.update_entry(key=key, value=value, source=source)

    def update_from_env(
        self,
        env_paths: Dict[str, Sequence[str]],
        converters: Optional[Dict[str, str]] = None,
        prefix: str = "",
    ) -> None:
        """Update the configuration from environment variables"""
        converters = {} if converters is None else converters

        # Apply prefix
        env_paths = {f"{prefix}{k}": v for k, v in env_paths.items()}
        converters = {f"{prefix}{k}": v for k, v in converters.items()}

        # Loop through the variables defined in the environment
        for var in set(os.environ) & set(env_paths):
            value = os.environ[var]

            # Convert type of value
            if var in converters:
                converter = converters[var]
                if callable(converter):
                    value = converter(value)
                else:
                    value = _converters.convert(f"to_{converter}", value=value)

            # Walk down tree for given entry
            entry = entry_tree = {}
            *entry_path, entry_key = env_paths[var]
            for key in entry_path:
                entry = entry.setdefault(key, {})
            entry[entry_key] = value

            # Update configuration with new entry
            self.update_from_dict(entry_tree, source=f"{var} (environment variable)")

    def update_from_file(
        self, file_path: Union[str, pathlib.Path], file_format: Optional[str] = None
    ) -> None:
        """Update the configuration from a file"""
        file_path = pathlib.Path(file_path).resolve()
        file_format = (
            readers.guess_format(file_path) if file_format is None else file_format
        )
        entries = readers.read(file_format, file_path=file_path)
        self.update_from_dict(entries, source=f"{file_path} ({file_format} reader)")

    def as_dict(self) -> Dict[str, Any]:
        """Convert Configuration to a  nested dictionary"""
        return {
            k: v.as_dict() if isinstance(v, self.__class__) else v
            for k, v in self.data.items()
        }

    @property
    def sections(self) -> List["Configuration"]:
        """List of sections in Configuration

        Only actual sections are included, not top level entries.
        """
        return [s for s in self.data.values() if isinstance(s, self.__class__)]

    @property
    def section_names(self) -> List[str]:
        """List names of sections in Configuration

        Only actual sections are included, not top level entries.
        """
        return [n for n, s in self.data.items() if isinstance(s, self.__class__)]

    @property
    def entries(self) -> List[Tuple[str, Any]]:
        """List of key, value entries in Configuration

        Only actual entries are included, not subsections.
        """
        return [
            (k, v) for k, v in self.data.items() if not isinstance(v, self.__class__)
        ]

    @property
    def entry_values(self) -> List[Any]:
        """List of values in Configuration

        Only actual values are included, not subsections.
        """
        return [v for v in self.data.values() if not isinstance(v, self.__class__)]

    @property
    def entry_keys(self) -> List[str]:
        """List of keys in Configuration

        Only actual keys are included, not subsections.
        """
        return [k for k, v in self.data.items() if not isinstance(v, self.__class__)]

    @property
    def sources(self):
        """List sources in configuration"""
        src = set(self._source.values())
        for section in self.sections:
            src |= section.sources

        return src

    def source(self, key):
        """List source for the given key"""
        if key in self.entry_keys:
            return self._source[key]
        elif key in self.section_names:
            return self[key].sources
        else:
            raise KeyError(f"Unknown entry {key!r}")

    def replace(
        self,
        key: str,
        *,
        converter: Optional[Callable[[str], Any]] = None,
        default: Optional[str] = None,
        **replace_vars: str,
    ) -> Any:
        """Replace values in an entry based on {} format strings"""
        all_vars = {**self.vars, **replace_vars}
        replaced = _replace(self.data[key], replace_vars=all_vars, default=default)
        if converter is not None:
            if isinstance(converter, str):
                replaced = _converters.convert(f"to_{converter}", value=replaced)
            else:
                replaced = converter(replaced)

        return replaced

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
            raise _exceptions.EntryError(f"{self.name}.{key!r} is a Configuration")

        return value

    @_dispatch_to(_converters.to_str)
    def to_str(self, key: str) -> str:
        """Convert entry to string"""
        return self._get_value(key)

    @_dispatch_to(_converters.to_int)
    def to_int(self, key: str) -> int:
        """Convert entry to integer number"""
        return self._get_value(key)

    @_dispatch_to(_converters.to_float)
    def to_float(self, key: str) -> float:
        """Convert entry to a floating point number"""
        return self._get_value(key)

    @_dispatch_to(_converters.to_bool)
    def to_bool(self, key: str) -> bool:
        """Convert entry to a boolean"""
        return self._get_value(key)

    @_dispatch_to(_converters.to_date)
    def to_date(self, key: str) -> date:
        """Convert entry to a date"""
        return self._get_value(key)

    @_dispatch_to(_converters.to_datetime)
    def to_datetime(self, key: str) -> datetime:
        """Convert entry to a datetime"""
        return self._get_value(key)

    @_dispatch_to(_converters.to_path)
    def to_path(self, key: str) -> pathlib.Path:
        """Convert entry to a path"""
        return self._get_value(key)

    @_dispatch_to(_converters.to_list)
    def to_list(self, key: str) -> List[Any]:
        """Convert entry to a list"""
        return self._get_value(key)

    @_dispatch_to(_converters.to_dict)
    def to_dict(self, key: str) -> Dict[str, Any]:
        """Convert entry to a dictionary"""
        return self._get_value(key)

    @_dispatch_to(_converters.to_set)
    def to_set(self, key: str) -> Set[Any]:
        """Convert entry to a set"""
        return self._get_value(key)

    @_dispatch_to(_converters.to_tuple)
    def to_tuple(self, key: str, **options: Any) -> Tuple[Any, ...]:
        """Convert entry to a tuple"""
        return self._get_value(key)

    #
    # Dunder methods
    #
    def __dir__(self) -> List[str]:
        """Add sections and entries to list of attributes"""
        return list(super().__dir__()) + list(self.data.keys())

    def __getattr__(self, key: str) -> Union["Configuration", Any]:
        return self[key]

    def __repr__(self):
        """Simple representation of a Configuration"""
        return f"{self.__class__.__name__}(name={self.name!r})"

    def __str__(self):
        """Full representation of a Configuration"""
        return self.as_str()


def _replace(
    string: str, replace_vars: Dict[str, str], default: Optional[str] = None
) -> str:
    """Replace format style variables in a string

    Handles nested replacements by first replacing the replace_vars. Format
    specifiers (after colon, :) are allowed, but can not contain nested format
    strings.

    This function is used instead of str.format for three reasons. It handles:
    - that not all pairs of {...} are replaced at once
    - optional default values for variables that are not specified
    - nested replacements where values of replace_vars may be replaced themselves

    Credit: Originally written for `midgard.config.Configuration`

    Args:
        string:        Original string
        replace_vars:  Variables that can be replaced
        default:       Optional default value used for vars not in replace_vars.
    """
    matches = re.finditer(r"\{(\w+)(:[^\{\}]*)?\}", string)
    for match in matches:
        var = match.group(1)
        var_expr = match.string[slice(*match.span())]
        replacement = replace_vars.get(var)
        if replacement is None:
            # Default replacements
            replacement = var_expr if default is None else default
        else:
            # Nested replacements
            replacement = _replace(replacement, replace_vars, default)

        # Use str.format to handle format specifiers
        string = string.replace(var_expr, var_expr.format(**{var: replacement}))

    return string
