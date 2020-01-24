"""Plugins for writing configuration file formats

"""

# Standard library imports
import pathlib
from typing import Any, Dict, Optional

# Third party imports
import pyplugs

# PyConfs imports
from pyconfs import formats

names = pyplugs.names_factory(__package__)
as_str = pyplugs.call_factory(__package__)


def as_file(
    config: Dict[str, Any],
    file_path: pathlib.Path,
    file_format: Optional[str] = None,
    encoding: str = "utf-8",
    **writer_args: Any,
) -> None:
    """Write dictionary to file with the given format

    If the file format is not specified, it is deduced from the file path suffix.
    """
    # Guess format
    file_format = (
        formats.guess_format(file_path) if file_format is None else file_format
    )

    # Write file
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(
        as_str(file_format, config=config, **writer_args), encoding=encoding
    )
