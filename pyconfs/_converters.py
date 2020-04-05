"""Functions that convert strings to other datatypes


"""

# Standard library imports
import functools
import os.path
import pathlib
import re
from datetime import date, datetime
from typing import Any, Callable, Dict, List, Set, Tuple

# Third party imports
import pyplugs

# PyConfs imports
from pyconfs import _exceptions

# Set up pyplugs plugins
package, _, plugin = __name__.rpartition(".")
convert = functools.partial(pyplugs.call, package, plugin)
info = functools.partial(pyplugs.info, package, plugin)
names = functools.partial(pyplugs.funcs, package, plugin)


# Mappings for conversion to booleans
_BOOLEAN_STATES = {
    "0": False,
    "1": True,
    "false": False,
    "true": True,
    "no": False,
    "yes": True,
    "off": False,
    "on": True,
}


def convert_to(dtype, value):
    """Convert value to the given type"""
    try:
        return convert(f"to_{dtype}", value=value)
    except pyplugs.UnknownPluginFunctionError:
        raise ValueError(f"Conversion to {dtype} is not supported")


@pyplugs.register
def to_str(value: str) -> str:
    """Convert value to a string"""
    return str(value)


@pyplugs.register
def to_int(value: str) -> int:
    """Convert value to an integer number"""
    return int(value)


@pyplugs.register
def to_float(value: str) -> float:
    """Convert value to a floating point number"""
    return float(value)


@pyplugs.register
def to_bool(value: str) -> bool:
    """Convert value to a boolean"""
    try:
        return _BOOLEAN_STATES[str(value).lower()]
    except KeyError:
        raise _exceptions.ConversionError(
            f"Value {value!r} can not be converted to boolean"
        ) from None


@pyplugs.register
def to_date(value: str, format="%Y-%m-%d") -> date:
    """Convert value to a date"""
    return datetime.strptime(str(value), format=format).date()


@pyplugs.register
def to_datetime(value: str, format="%Y-%m-%d %H:%M:%S") -> datetime:
    """Convert value to a datetime"""
    return datetime.strptime(str(value), format=format)


@pyplugs.register
def to_path(value: str) -> pathlib.Path:
    """Convert value to a path"""
    # Handle ~ shortcut for home directories
    if "~" in value:
        value = os.path.expanduser(value)

    return pathlib.Path(value)


@pyplugs.register
def to_list(
    value: str,
    split_re: str = r"[\s,]+",
    converter: Callable[[str], Any] = str,
    max_split: int = 0,
) -> List[Any]:
    """Convert value to a list"""
    return [
        converter(s) for s in re.split(split_re, str(value), maxsplit=max_split) if s
    ]


@pyplugs.register
def to_dict(
    value: str,
    item_split_re: str = r",\n?",
    key_value_split_re: str = r"[:]",
    converter: Callable[[str], Any] = str.strip,
    max_split: int = 0,
) -> Dict[str, Any]:
    """Convert value to a dictionary"""
    items = [
        re.split(key_value_split_re, s, maxsplit=1)
        for s in re.split(item_split_re, str(value), maxsplit=max_split)
        if s
    ]
    return {k: converter(v) for k, v in items}


@pyplugs.register
def to_set(
    value: str,
    split_re: str = r"[\s,]+",
    converter: Callable[[str], Any] = str,
    max_split: int = 0,
) -> Set[Any]:
    """Convert value to a set"""
    return {
        converter(s) for s in re.split(split_re, str(value), maxsplit=max_split) if s
    }


@pyplugs.register
def to_tuple(
    value: str,
    split_re: str = r"[\s,]+",
    converter: Callable[[str], Any] = str,
    max_split: int = 0,
) -> Tuple[Any, ...]:
    """Convert value to a tuple"""
    return tuple(
        converter(s) for s in re.split(split_re, str(value), maxsplit=max_split) if s
    )
