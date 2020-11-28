"""Types that a configuration can be converted to"""

# Standard library imports
import re
from typing import Any, NamedTuple, Optional

# Third party imports
import pyplugs

# Find plugins in the current file
PACKAGE, _, PLUGIN = __name__.rpartition(".")


def add_to_class(cls):
    """Add all type converters as methods on the given class"""
    for func in pyplugs.funcs(PACKAGE, PLUGIN):
        setattr(cls, func, pyplugs.get(PACKAGE, PLUGIN, func=func))


@pyplugs.register
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
    src_map = {k: None if k in self.data else f"{k}={v!r}" for k, v in tpl_data.items()}

    # Create a NamedTuple template based on the current data in the Configuration
    if template is None:
        template = NamedTuple(self.name, **{k: type(v) for k, v in tpl_data.items()})

    # Use NamedTuple to validate fields
    try:
        tpl = template(**tpl_data)
    except TypeError as err:
        # Rewrite the error message if fields are missing
        name = f"Configuration {self.name!r}"
        message = err.args[0].replace("__new__()", name).replace("<lambda>()", name)
        field = (re.findall(r"'([^']+)'$", message) or ["__no_field_found__"]).pop()
        message += f" ({self._get_source_string(field, src_map.get(field))})"
        err.args = (message, *err.args[1:])
        raise

    # Check that types are correct
    if not hasattr(tpl, "__annotations__"):
        return tpl

    for field, field_type in tpl.__annotations__.items():
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
