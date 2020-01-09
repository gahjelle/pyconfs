"""Writer for ini-files based on ConfigParser


"""

# Standard library imports
import pathlib
from configparser import ConfigParser
from typing import Any, Dict

# Third party imports
import pyplugs

_SUFFIXES = {".ini", ".cfg", ".conf"}
_TYPE_SUFFIX = ":type"


@pyplugs.register
def write_ini_file(
    config: Dict[str, Any], file_path: pathlib.Path, keep_types: bool = False
) -> None:
    """Use ConfigParser to write an ini-file"""
    cfg = ConfigParser(delimiters=("=",))
    cfg.update(_normalize(config, keep_types=keep_types))

    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open(mode="w") as fid:
        cfg.write(fid)


def _normalize(config: Dict[str, Any], keep_types: bool) -> Dict[str, Dict[str, str]]:
    """ConfigParser only supports string values and 1 level of nesting"""
    if keep_types:
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


@pyplugs.register
def is_format(file_path: pathlib.Path) -> bool:
    """Is the given file of ini-format?"""
    return file_path.suffix in _SUFFIXES
