"""A PyConfs Configuration

The `Configuration` is a dictionary structure containing configuration entries,
possibly nested inside sections. Each section is its own `Configuration` as
well.
"""

# Standard library imports
import functools
import os
import pathlib
import textwrap
import warnings
from collections import UserDict, UserList, UserString
from datetime import date, datetime
from typing import Any, Callable, Dict, List, Optional, Sequence, Set, Tuple, Union

# PyConfs imports
from pyconfs import _converters, _exceptions, _types, readers, writers


def _dispatch_to(converter):
    """Decorator for dispatching methods to converter functions

    This outer closure stores the converter parameter.
    """

    def _decorator_dispatch_to(func):
        """Decorate the given function"""

        @functools.wraps(func)
        def _wrapper_dispatch_to(self, key: str, **options):
            """Call the converter function"""
            return converter(value=func(self, key), **options)

        return _wrapper_dispatch_to

    return _decorator_dispatch_to


class IsConfiguration:
    """Mixin used to identify Configuration objects"""


class Configuration(UserDict, IsConfiguration):
    """Consistent handling of configuration formats

    Credit: Originally written for `midgard.config.Configuration`.
            See https://github.com/kartverket/midgard
    """

    __slots__ = ("data", "name", "vars", "_source")

    def __init__(
        self, name: Optional[str] = None, _vars: Optional[Dict[str, str]] = None
    ) -> None:
        """Create an empty configuration"""
        super().__init__()
        self.name = name
        self.vars = {} if _vars is None else _vars
        self._source = {}

    @classmethod
    def from_dict(
        cls, entries: Dict[str, Any], *, name: Optional[str] = None, source: str = ""
    ) -> "Configuration":
        """Create a Configuration from a dictionary"""
        cfg = cls(name=name)
        cfg.update_from_dict(entries, source=source)
        return cfg

    @classmethod
    def from_file(
        cls,
        file_path: Union[str, pathlib.Path],
        file_format: Optional[str] = None,
        *,
        name: Optional[str] = None,
        encoding: str = "utf-8",
        **reader_args: Any,
    ) -> "Configuration":
        """Create a Configuration from a file"""
        file_path = pathlib.Path(file_path)

        cfg = cls(name=name)
        cfg.update_from_file(
            file_path=file_path, file_format=file_format, **reader_args
        )
        return cfg

    @classmethod
    def from_str(
        cls, string: str, format: str, *, name: Optional[str] = None
    ) -> "Configuration":
        """Create a Configuration from a string"""
        cfg = cls(name=name)
        cfg.update_from_str(string, format=format)
        return cfg

    def update_entry(self, key: str, value: Any, source: str = "") -> None:
        """Update one entry in configuration"""
        name = key if self.name is None else f"{self.name}.{key}"

        # Treat dicts as nested configurations
        if isinstance(value, (dict, UserDict)):
            self.data.setdefault(key, self.__class__(name=name, _vars=self.vars))
            self.data[key].update_from_dict(value, source=source)

        # Treat lists with nested elements as configuration lists
        elif isinstance(value, (list, UserList)) and _is_nested(value):
            self.data.setdefault(key, ConfigurationList(name=name, _vars=self.vars))
            self.data[key].update_from_list(value, source=source)

        else:
            self.data[key] = value
            self._source[key] = source

    def update_from_dict(self, entries: Dict[str, Any], source: str = "") -> None:
        """Update the configuration from a dictionary"""
        for key, value in entries.items():
            self.update_entry(key=key, value=value, source=source)

    def update_from_config(
        self, key: str, config: IsConfiguration, source: str = ""
    ) -> None:
        """Update the configuration from another configuration"""

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
                try:
                    if callable(converter):
                        value = converter(value)
                    else:
                        value = _converters.convert(f"to_{converter}", value=value)
                except ValueError:
                    warnings.warn(
                        RuntimeWarning(
                            f"Could not convert {var}={value!r} using {converter}"
                        ),
                        stacklevel=2,
                    )
                    break

            # Walk down tree for given entry
            entry = entry_tree = {}
            *entry_path, entry_key = env_paths[var]
            for key in entry_path:
                entry = entry.setdefault(key, {})
            entry[entry_key] = value

            # Update configuration with new entry
            self.update_from_dict(entry_tree, source=f"{var} (environment variable)")

    def update_from_file(
        self,
        file_path: Union[str, pathlib.Path],
        file_format: Optional[str] = None,
        encoding: str = "utf-8",
        **reader_args: Any,
    ) -> None:
        """Update the configuration from a file"""
        file_path = pathlib.Path(file_path)
        file_format, entries = readers.from_file(
            file_path=file_path, file_format=file_format, **reader_args
        )
        self.update_from_dict(
            entries, source=f"{file_path.resolve()} ({file_format.upper()} reader)"
        )

    def update_from_str(self, string: str, format: str, *, source=None) -> None:
        """Update the configuration from a string"""
        if source is None:
            string_repr = f"{string[:30]} ..." if len(string) > 32 else string
            source = f"String: {string_repr} ({format} reader)"

        entries = readers.from_str(format, string=string)
        self.update_from_dict(entries, source=source)

    def get(self, key, default=None):
        """Get a value from the configuration, allow nested keys"""
        if isinstance(key, list):
            first_key, *tail_keys = key
            value = super().get(first_key, default)
            if tail_keys:
                try:
                    return value.get(list(tail_keys), default)
                except AttributeError:
                    return default
            else:
                return value
        else:
            return super().get(key, default)

    @property
    def name_stem(self) -> str:
        """Part of name after last dot"""
        if self.name is None:
            return ""

        return self.name.rpartition(".")[-1]

    @property
    def section_items(self) -> List[Tuple[str, "Configuration"]]:
        """List of section names and sections in Configuration

        Only actual sections are included, not top level entries.
        """
        return list(self._section_items())

    @property
    def sections(self) -> List["Configuration"]:
        """List of sections in Configuration

        Only actual sections are included, not top level entries.
        """
        return [s for n, s in self._section_items()]

    @property
    def section_names(self) -> List[str]:
        """List names of sections in Configuration

        Only actual sections are included, not top level entries.
        """
        return [n for n, s in self._section_items()]

    def _section_items(self) -> List[Tuple[str, "Configuration"]]:
        """Generator of section names and sections in Configuration

        Only actual sections are included, not top level entries.
        """
        for section_name, section in self.data.items():
            if isinstance(section, IsConfiguration):
                for flattened_section in section._flatten_section():
                    yield section_name, flattened_section

    def _flatten_section(self) -> List["Configuration"]:
        """Return configuration as a list of one configuration"""
        return [self]

    @property
    def entries(self) -> List[Tuple[str, Any]]:
        """List of key, value entries in Configuration

        Only actual entries are included, not subsections.
        """
        return [
            (k, v) for k, v in self.data.items() if not isinstance(v, IsConfiguration)
        ]

    @property
    def entry_values(self) -> List[Any]:
        """List of values in Configuration

        Only actual values are included, not subsections.
        """
        return [v for v in self.data.values() if not isinstance(v, IsConfiguration)]

    @property
    def entry_keys(self) -> List[str]:
        """List of keys in Configuration

        Only actual keys are included, not subsections.
        """
        return [k for k, v in self.data.items() if not isinstance(v, IsConfiguration)]

    @property
    def leafs(self) -> List[Tuple["Configuration", str, Any]]:
        """List of all keys and values, recursively including subsections"""
        return list(self._leafs())

    @property
    def leaf_keys(self) -> List[Tuple["Configuration", str]]:
        """List of all keys in Configuration, recursively including subsections"""
        return [(s, k) for s, k, v in self._leafs()]

    @property
    def leaf_values(self) -> List[Any]:
        """List of all values in Configuration, recursively including subsections"""
        return [v for s, k, v in self._leafs()]

    def _leafs(self) -> List[Tuple["Configuration", str, Any]]:
        """Generator of all keys and values, recursively including subsections"""
        for key, value in self.data.items():
            if isinstance(value, IsConfiguration):
                yield from value._leafs()
            else:
                yield self, key, value

    @property
    def sources(self):
        """List sources in configuration"""
        src = set(self._source.values())
        for section in self.sections:
            src |= section.sources

        return src

    def get_source(self, key):
        """List source for the given key"""
        if key in self.entry_keys:
            return self._source[key]
        elif key in self.section_names:
            return self[key].sources
        else:
            raise KeyError(f"Unknown entry {key!r}")

    def _get_source_string(self, key: str, fallback: Optional[str] = None) -> str:
        """Format source or sources as a string, be lenient about missing keys"""
        if key in self:
            return self.get_source(key)
        elif fallback is None:
            return ", ".join(self.sources)
        else:
            return fallback

    def replace(
        self,
        key: str,
        *,
        converter: Optional[Callable[[str], Any]] = None,
        dedent: bool = False,
        default: Optional[str] = None,
        **replace_vars: str,
    ) -> Any:
        """Replace values in an entry based on {} format strings"""
        all_vars = Variables(**self.vars, **replace_vars, default=default)
        value = textwrap.dedent(self.data[key]) if dedent else self.data[key]

        # Replace variables
        replaced = value.format_map(all_vars)

        # Optionally convert value to a different data type
        if converter is None:
            return replaced
        elif callable(converter):
            return converter(replaced)
        else:
            return _converters.convert(f"to_{converter}", value=replaced)

    def as_dict(self, **other_fields: Any) -> Dict[str, Any]:
        """Convert Configuration to a nested dictionary"""
        dct_data = {**self.data, **other_fields}
        return {
            k: v.as_dict() if isinstance(v, IsConfiguration) else v
            for k, v in dct_data.items()
        }

    def as_str(
        self,
        format: Optional[str] = None,
        *,
        indent: int = 2,
        key_width: int = 20,
        skip_header: bool = False,
        **writer_args: Any,
    ) -> str:
        """Represent Configuration as a string, heavily inspired by TOML"""
        if format is not None:
            return writers.as_str(format, config=self.as_dict(), **writer_args)

        lines = [] if self.name is None or skip_header else [f"[{self.name}]"]
        for key, value in self.data.items():
            if isinstance(value, IsConfiguration):
                value_str = value.as_str(indent=indent, key_width=key_width)
                lines.append("\n" + textwrap.indent(value_str, " " * indent))
            else:
                lines.append(f"{key:<{key_width}} = {_repr_toml(value)}")
        return "\n".join(lines)

    def as_file(
        self,
        file_path: Union[str, pathlib.Path],
        file_format: Optional[str] = None,
        encoding: str = "utf-8",
        **writer_args: Any,
    ):
        """Write Configuration to a file"""
        writers.as_file(
            config=self.as_dict(),
            file_path=pathlib.Path(file_path),
            file_format=file_format,
            encoding=encoding,
            **writer_args,
        )

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
        """Get sections and keys using attribute (dot) syntax"""
        try:
            return self[key]
        except KeyError:
            raise AttributeError(
                f"Configuration {self.name} has no entry {key!r}"
            ) from None

    def __setattr__(self, key: str, value: Any) -> None:
        """Update an entry using assignment syntax on attributes"""
        if key in self.__slots__:
            # Update regular attributes as normal
            super().__setattr__(key, value)
        else:
            self.update_entry(key=key, value=value)

    def __setitem__(self, key: str, value: Any) -> None:
        """Update an entry using assignment syntax on items"""
        self.update_entry(key=key, value=value)

    def __repr__(self):
        """Simple representation of a Configuration"""
        if self.name is None:
            return f"{self.__class__.__name__}()"
        else:
            return f"{self.__class__.__name__}(name={self.name!r})"

    def __str__(self):
        """Full representation of a Configuration"""
        return self.as_str()


# Add converters to other types to Configuration
_types.add_to_class(Configuration)


class ConfigurationList(UserList, IsConfiguration):
    """Collect a list of Configurations in one object"""

    def __init__(
        self, name: Optional[str] = None, _vars: Optional[Dict[str, str]] = None
    ) -> None:
        """Create an empty configuration"""
        super().__init__()
        self.name = name
        self.vars = {} if _vars is None else _vars
        self._source = []

    @classmethod
    def from_list(
        cls, entries: List[Any], *, name: Optional[str] = None, source: str = ""
    ) -> "ConfigurationList":
        """Create a ConfigurationList from a list"""
        cfg = cls(name=name)
        cfg.update_from_list(entries, source=source)
        return cfg

    def update_entry(self, value: Any, source: str = "") -> None:
        """Add one entry to the configuration list"""
        # Treat dicts as nested configurations
        if isinstance(value, dict):
            value = Configuration.from_dict(value, name=self.name, source=source)
            source = value._source

        # Treat lists with nested elements as configuration lists
        elif isinstance(value, list) and _is_nested(value):
            value = ConfigurationList.from_list(value, name=self.name, source=source)
            source = value._source

        # Add entry to configuration list
        self.data.append(value)
        self._source.append(source)

    def update_from_list(self, entries: List[Any], source: str = "") -> None:
        """Update the configuration list from a list"""
        for entry in entries:
            self.update_entry(entry, source=source)

    def _flatten_section(self) -> List["Configuration"]:
        """Return configuration as a list of Configurations"""
        return self.data

    def get(self, key, default=None):
        """Get an entry from the ConfigurationList, allow nested keys"""
        if isinstance(key, list):
            first_key, *tail_keys = key
            value = self.get(first_key, default)
            if tail_keys:
                try:
                    return value.get(list(tail_keys), default)
                except AttributeError:
                    return default
            else:
                return value
        else:
            try:
                return self[key]
            except (IndexError, AttributeError):
                return default

    @property
    def leafs(self) -> List[Tuple["Configuration", str, Any]]:
        """List of all keys and values, recursively including subsections"""
        return list(self._leafs())

    @property
    def leaf_keys(self) -> List[Tuple["Configuration", str]]:
        """List of all keys in Configuration, recursively including subsections"""
        return [(s, k) for s, k, v in self._leafs()]

    @property
    def leaf_values(self) -> List[Any]:
        """List of all values in Configuration, recursively including subsections"""
        return [v for s, k, v in self._leafs()]

    def _leafs(self) -> List[Tuple["Configuration", str, Any]]:
        """Generator of all keys and values, recursively including subsections"""
        for value in self:
            if isinstance(value, IsConfiguration):
                yield from value._leafs()
            else:
                yield self, self.name, value

    def as_dict(self) -> List[Any]:
        """Convert ConfigurationList to a nested dictionary"""
        return [v.as_dict() if isinstance(v, IsConfiguration) else v for v in self.data]

    def as_str(self, *, indent: int = 2, key_width: int = 20) -> str:
        """Represent configuration list as a string"""
        lines = []
        for value in self.data:
            lines.append(f"\n[[{self.name}]]")
            if isinstance(value, IsConfiguration):
                value_str = value.as_str(
                    indent=indent, key_width=key_width, skip_header=True
                )
                lines.append(value_str)
            else:
                lines.append(f"{_repr_toml(value)}")
        return "\n".join(lines).strip()

    #
    # Dunder methods
    #
    def __getattr__(self, key: str) -> Union["ConfigurationList", Any]:
        """Include attributes available on all entries"""
        try:
            return self.from_list(getattr(entry, key) for entry in self.data)
        except AttributeError:
            raise AttributeError(
                f"{self.__class__.__name__!r} object has no attribute {key!r}"
            ) from None

    def __getitem__(self, key: Union[int, str]) -> Union["ConfigurationList", Any]:
        """Include items available on all entries"""
        try:
            return super().__getitem__(key)
        except TypeError:
            try:
                return self.from_list(entry[key] for entry in self.data)
            except KeyError:
                raise AttributeError(
                    f"All items in ConfigurationList {self.name} "
                    f"don't have entry {key!r}"
                ) from None


class Variables(UserDict):
    """Dictionary that allows more flexible format style replacements

    Instead of using str.format(**dict), you can use str.format_map(Variables)

    This will handle:
    - that not all pairs of {...} are replaced at once
    - optional default values for variables that are not specified
    - nested replacements where values of replace_vars may be replaced
      themselves
    """

    def __init__(self, default=None, **vars):
        """Store optional default value"""
        super().__init__(**vars)
        self.default = default

    def __getitem__(self, key):
        """Handle nested replacements"""
        value = super().__getitem__(key)

        # Nested replacement for strings
        if isinstance(value, str):
            return value.format_map(self)
        else:
            return value

    def __missing__(self, key):
        """Handle missing variables"""
        return UnsetVariable(key) if self.default is None else self.default


class UnsetVariable(UserString):
    """Variable that does not have a value yet, used by Variables"""

    def __format__(self, fmt):
        """Keep the formatting string"""
        if fmt:
            return f"{{{self.data}:{fmt}}}"
        else:
            return str(self)

    def __str__(self):
        """Represent unset variables by adding curly braces that can be parsed later"""
        return f"{{{self.data}}}"


def _repr_toml(value: Any) -> str:
    """Represent value as a TOML string"""

    # Use double quotes for strings
    if isinstance(value, str):
        if "\n" in value:
            # Use triple quotes for multi-line strings
            return f'"""\n{value}"""'
        else:
            return f'"{value}"'

    # Dates can be written using isoformat
    if isinstance(value, (date, datetime)):
        return value.isoformat()

    # Bools should be written true and false
    if isinstance(value, bool):
        return repr(value).lower()

    # Handle lists recursively
    if isinstance(value, (list, tuple)):
        return f"[{', '.join(_repr_toml(v) for v in value)}]"

    return str(value)


def _is_nested(sequence) -> bool:
    """Check if the sequence contains nested lists or dictionaries"""
    return any(isinstance(s, (dict, list, IsConfiguration)) for s in sequence)
