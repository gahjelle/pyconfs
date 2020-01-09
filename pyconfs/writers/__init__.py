"""Plugins for writing configuration file formats


"""

# Standard library imports
import pathlib
from typing import Any, Dict

# Third party imports
import pyplugs

# PyConfs imports
from pyconfs._exceptions import UnknownFormat

names = pyplugs.names_factory(__package__)
as_str = pyplugs.call_factory(__package__)


def write(
    config: Dict[str, Any],
    file_path: pathlib.Path,
    file_format=None,
    **writer_args: Any,
) -> None:
    """Write dictionary to file with the given format

    If the file format is not specified, it is deduced from the file path suffix.
    """
    # Guess format
    file_format = guess_format(file_path) if file_format is None else file_format

    # Write file
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(as_str(file_format, config=config, **writer_args))


def guess_format(file_path: pathlib.Path) -> str:
    """Guess the format of a file based on the file path suffix"""
    for writer in names():
        if pyplugs.call(__package__, writer, func="is_format", file_path=file_path):
            return writer

    raise UnknownFormat(f"Could not guess format of {file_path}")
