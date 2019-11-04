"""Utility functions for pyconfs
"""

# Standard library imports
import importlib
import pathlib
import sys
from types import ModuleType
from typing import Any, Optional


class FuturePackage:
    """Represents a package that will be imported in the future"""

    _pip_names = {"toml": "toml", "yaml": "PyYAML"}

    def __init__(self, package_name: str) -> None:
        self._package_name = package_name
        self._package: Optional[ModuleType] = None

    def __getattr__(self, key: str) -> Any:
        """Dispatch attribute call to underlying package"""
        if self._package is None:
            self._import_package()

        return getattr(self._package, key)

    def _import_package(self) -> None:
        """Import the underlying package.

        Give proper error message if package is not available
        """
        try:
            self._package = importlib.import_module(self._package_name)
        except ImportError as err:
            msg = f"Could not import {self._package_name!r}."
            pip_name = self._pip_names.get(self._package_name)
            if pip_name:
                py = pathlib.Path(sys.executable).name
                msg += f" Install it using '{py} -m pip install {pip_name}'"

            raise err.__class__(msg) from None


def delayed_import(package_name: str) -> FuturePackage:
    """Delay import until package is used.

    This helps users not having to install dependencies for formats they don't
    use.

    Args:
        package_name  - Name of package that will be imported

    Returns:
        FuturePackage that resolves to package when it's used
    """
    return FuturePackage(package_name)
