# PyConfs

_Unified handling of configuration files in Python_

[![Latest version](https://img.shields.io/pypi/v/pyconfs.svg)](https://pypi.org/project/pyconfs/)
[![Python versions](https://img.shields.io/pypi/pyversions/pyconfs.svg)](https://pypi.org/project/pyconfs/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Interrogate DocStrings](https://github.com/gahjelle/pyconfs/blob/main/docs/images/interrogate_badge.svg)](https://interrogate.readthedocs.io/)
[![unit_tests](https://github.com/gahjelle/pyconfs/workflows/unit_tests/badge.svg)](https://github.com/gahjelle/pyconfs/actions)

## Installing PyConfs

PyConfs is available at [PyPI](https://pypi.org/project/pyconfs/). You can install it using Pip:

    $ python -m pip install pyconfs


## Using PyConfs

A **PyConfs Configuration** is a dictionary-like object that unifies several different configuration file formats, including INI, JSON, TOML, and YAML.

**Read a configuration from file**:

    from pyconfs import Configuration
    cfg = Configuration.from_file("sample.json")

**Access entries in a configuration**:

    package_name = cfg.name
    first_name = cfg.author.firstname


## Installing From Source

You can always download the [latest version of PyConfs from GitHub](https://github.com/gahjelle/pyconfs). PyConfs uses [Flit](https://flit.readthedocs.io/) as a setup tool.

To install PyConfs from the downloaded source, run Flit:

    $ python -m flit install --deps production

If you want to change and play with the PyConfs source code, you should install it in editable mode:

    $ python -m flit install --symlink