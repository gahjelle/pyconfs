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
import warnings
from collections import UserDict
from datetime import date, datetime
from typing import (
    Any,
    Callable,
    Dict,
    List,
    NamedTuple,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
)

# PyConfs imports
from pyconfs import _converters, _exceptions, readers, writers

# Marker for missing keys
MISSING = object()


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
        if isinstance(value, dict):
            # Treat dicts as nested configurations
            name = key if self.name is None else f"{self.name}.{key}"
            self.data.setdefault(key, self.__class__(name=name, _vars=self.vars))
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
        entries = readers.from_file(
            file_path=file_path, file_format=file_format, **reader_args
        )
        self.update_from_dict(
            entries, source=f"{file_path.resolve()} ({file_format} reader)"
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
    def section_items(self) -> List[Tuple[str, "Configuration"]]:
        """List of section names and sections in Configuration

        Only actual sections are included, not top level entries.
        """
        return [(n, s) for n, s in self.data.items() if isinstance(s, self.__class__)]

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
    def leafs(self) -> List[Tuple["Configuration", str, Any]]:
        """Generator of all keys and values, recursively including subsections"""
        for key, value in self.data.items():
            if isinstance(value, self.__class__):
                yield from value.leafs
            else:
                yield self, key, value

    @property
    def leaf_keys(self) -> List[Tuple["Configuration", str]]:
        """Generator of all keys in Configuration, recursively including subsections"""
        for key, value in self.data.items():
            if isinstance(value, self.__class__):
                yield from value.leaf_keys
            else:
                yield self, key

    @property
    def leaf_values(self) -> List[Any]:
        """Generator of values in Configuration, recursively including subsections"""
        for key, value in self.data.items():
            if isinstance(value, self.__class__):
                yield from value.leaf_values
            else:
                yield value

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
        all_vars = {**self.vars, **replace_vars}
        value = self.get(key, MISSING)
        if value is MISSING:
            raise KeyError(key)

        # Replace variables
        value = textwrap.dedent(value) if dedent else value
        replaced = _replace(value, replace_vars=all_vars, default=default)

        # Optionally convert value to a different data type
        if converter is not None:
            if callable(converter):
                replaced = converter(replaced)
            else:
                replaced = _converters.convert(f"to_{converter}", value=replaced)

        return replaced

    def as_dict(self, **other_fields: Any) -> Dict[str, Any]:
        """Convert Configuration to a nested dictionary"""
        dct_data = {**self.data, **other_fields}
        return {
            k: v.as_dict() if isinstance(v, self.__class__) else v
            for k, v in dct_data.items()
        }

    def as_str(
        self,
        format: Optional[str] = None,
        *,
        indent: int = 2,
        key_width: int = 20,
        **writer_args: Any,
    ) -> str:
        """Represent Configuration as a string, heavily inspired by TOML"""
        if format is not None:
            return writers.as_str(format, config=self.as_dict(), **writer_args)

        lines = [] if self.name is None else [f"[{self.name}]"]
        for key, value in self.data.items():
            if isinstance(value, self.__class__):
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

    def as_named_tuple(
        self, template: Optional[NamedTuple] = None, **other_fields: Any
    ) -> NamedTuple:
        """Convert Configuration to a named tuple

        If a typed NamedTuple is given as a template, then the configuration
        will be validated against that template.

        Any other fields that are supplied will be added to the named tuple in
        addition to the data in the configuration.
        """
        tpl_data = {**self.data, **other_fields}
        src_map = {
            k: None if k in self.data else f"{k}={v!r}" for k, v in tpl_data.items()
        }

        # Create a NamedTuple template based on the current data in the Configuration
        if template is None:
            template = NamedTuple(
                self.name, fields=[(k, type(v)) for k, v in tpl_data.items()]
            )

        # Use NamedTuple to validate fields
        try:
            tpl = template(**tpl_data)
        except TypeError as err:
            # Rewrite the error message if fields are missing
            message = err.args[0].replace("__new__()", f"Configuration {self.name!r}")
            field = (re.findall(r"'([^']+)'$", message) or ["__no_field_found__"]).pop()
            message += f" ({self._get_source_string(field, src_map.get(field))})"
            err.args = (message, *err.args[1:])
            raise

        # Check that types are correct
        if not hasattr(tpl, "_field_types"):
            return tpl

        for field, field_type in tpl._field_types.items():
            if field not in tpl_data:
                continue

            try:
                is_correct_type = isinstance(tpl_data[field], field_type)
            except TypeError:
                # Not all types (e.g. subscripted generics) support isinstance checks
                continue

            if not is_correct_type:
                message = (
                    f"Configuration {self.name} got {type(tpl_data[field]).__name__!r} "
                    f"type for field {field}. "
                    f"{template.__name__} requires {field_type.__name__!r} "
                    f"({self._get_source_string(field, src_map.get(field))})"
                )
                raise TypeError(message)

        return tpl

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
        try:
            return self[key]
        except KeyError:
            raise AttributeError(
                f"Configuration {self.name} has no entry {key!r}"
            ) from None

    def __repr__(self):
        """Simple representation of a Configuration"""
        if self.name is None:
            return f"{self.__class__.__name__}()"
        else:
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
    - nested replacements where values of replace_vars may be replaced
      themselves

    Credit: Originally written for `midgard.config.Configuration`.
            See https://github.com/kartverket/midgard

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
            if default is None:
                continue
            replacement = default
        else:
            # Nested replacements
            if isinstance(replacement, str):
                replacement = _replace(replacement, replace_vars, default)

        # Use str.format to handle format specifiers
        string = string.replace(var_expr, var_expr.format(**{var: replacement}))

    return string


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
