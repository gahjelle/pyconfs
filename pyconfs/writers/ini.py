"""Writer for ini-files based on ConfigParser


"""

# Standard library imports
import io
from configparser import ConfigParser
from typing import Any, Dict

# Third party imports
import pyplugs

_TYPE_SUFFIX = ":type"


@pyplugs.register
def as_ini(config: Dict[str, Any], store_types: bool = False, **ini_args: Any) -> None:
    """Use ConfigParser to write an ini-file"""
    cfg = ConfigParser(delimiters=("=",))
    cfg.update(_normalize(config, store_types=store_types))

    # Write to a string
    with io.StringIO() as string:
        cfg.write(string, **ini_args)
        return string.getvalue()


def _normalize(config: Dict[str, Any], store_types: bool) -> Dict[str, Dict[str, str]]:
    """ConfigParser only supports string values and 1 level of nesting"""
    if store_types:
        raise NotImplementedError("Handling of types is not implemented in ini-writer")

    normalized = {}
    for section_name, section in config.items():
        if isinstance(section, dict):
            norm_section = normalized.setdefault(section_name, {})
            for key, entry in section.items():
                norm_section.update(_as_str(key, entry))
        elif isinstance(section, list):
            raise NotImplementedError(
                "Ini-writer does not handle top-level list configurations"
            )
        else:
            # Add section around top-level items
            normalized[section_name] = {section_name: str(section)}

    return normalized


def _as_str(key: str, entry: Any) -> Dict[str, str]:
    """Convert an entry to a string"""
    if isinstance(entry, dict):
        values = {}
        for subkey, subentry in entry.items():
            values.update(_as_str(f"{key}__{subkey}", subentry))
        return values
    elif isinstance(entry, list):
        return {key: ", ".join(str(item) for item in entry)}
    else:
        return {key: str(entry)}
