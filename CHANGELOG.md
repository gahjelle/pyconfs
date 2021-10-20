# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]

## [0.5.5] - 2021-10-20

### Fixed

- `ConfigurationList` objects do not preserve variables ([#20])


## [0.5.4] - 2021-10-18

### Added

- Changelog.
- `.is_list` property identifying `ConfigurationList` objects ([#19])


## [0.5.3] - 2021-10-16

### Added

- Explicit support for Python 3.9 ([#13]).
- [Citation file](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-citation-files) (by [@lewiuberg](https://github.com/lewiuberg/) in [#16]).
- Use GitHub actions for CD ([#18]).

### Fixed

- Enforce keys to be strings when writing to TOML (by [@lewiuberg](https://github.com/lewiuberg/) in [#17]).
- Fix error message in `.as_namedtuple()` for Python 3.10.


## [0.5.2] - 2021-06-08

### Fixed

- Handle nested (list) keys in `.replace()` ([#12]).


## [0.5.1] - 2020-11-28

### Changed

- Use GitHub actions for CI ([#8]).

### Removed

- `.copy_section()` ([#11]).

### Fixed

- Handle `.as_named_tuple()` in Python 3.9.
- Reporting correct name of reader in `.source` ([#9]).


## [0.5.0] - 2020-06-22

### Added

- `.copy_section()` to support default sections ([#7]).

### Changed

- Improved handling of variable interpolation in `.replace()` ([#3]).

### Fixed

- Properly update configuration, also when `cfg.entry = "value"` is used instead of `cfg.update_entry()` ([#4]).


## [0.4.2] - 2020-04-28

### Fixed

- Properly handle updating from nested dictionaries.


## [0.4.1] - 2020-04-20

### Fixed

- `.section_names` include parent names as well. Should just be the name of the actual section.


## [0.4.0] - 2020-04-18

### Added

- Proper support for lists inside configurations ([#1]).

### Changed

- `.leafs`, `.leaf_keys`, `.leaf_values` return lists for consistency with section and entry properties.


## [0.3.3] - 2020-04-05

### Added

- Explicit support for Python 3.9.
- Stand-alone `convert_to()` function exposing converters.
- `pretty_print` parameter when writing to TOML with nicer formatting.

### Changed

- Default `str()` behavior uses TOML format.
- `.get()` with list keys will recursively get an entry from a nested configuration.

### Fixed

- Allow `replace()` to handle non-strings by implictly converting variable values to strings.


## [0.3.2] - 2020-02-19

### Added

- `.leafs`, `.leaf_keys`, `.leaf_values` to iterate over all entries in a nested configuration.

### Changed

- Simplified support of multi-document YAMLs by only reading the first document.
- Ignore environment variables where conversion fails.


## [0.3.1] - 2020-01-24

### Added

- Support encodings in configuration files.


## [0.3.0] - 2020-01-09

### Added

- `.section_items` property to iterate over section names and section content.
- Reading configurations directly from strings.
- Writers for all supported configuration formats (INI, YAML, JSON, TOML).
- `.as_file()` for writing configurations to files.
- `.as_str()` for writing configurations to strings.

### Fixed

- Proper handling of AttributeErrors.


## [0.2.1] - 2019-11-12

### Changed

- Show parents in nested configuration names.
- Allow adding fields when converting to named tuples, dictionaries and strings.


## [0.2.0] - 2019-11-11

### Added

- Convert configurations to named tuples.
- Use named tuples for validation of configuration structure.


## [0.1.4] - 2019-11-04

### Added

- Handle `.cfg` files as INI-files.

### Fixed

- Don't crash when reading environment variables without converters.


## [0.1.3] - 2019-10-29

### Added

- Support JSON files using `json`.
- Support reading from environment variables.

### Changed

- TOML and YAML dependencies are installed as extras.


## [0.1.2] - 2019-10-22

### Added

- Support TOML files using 3rd party `toml`.
- Support YAML files using 3rd party`PyYAML`.
- Add source information to entries.

### Changed

- Only import 3rd party libraries when they are actually used.


## [0.1.1] - 2019-10-17

### Added

- Variable interpolation using `{}` handled by `.replace().
- Data type converters when using `.replace()` for entries.
- Support INI files using `configparser`.

### Fixed

- Actually return converted entries.


## [0.1.0] - 2019-10-16

Initial commit.

[Unreleased]: https://github.com/gahjelle/pyconfs/compare/v0.5.5...HEAD
[0.5.5]: https://github.com/gahjelle/pyconfs/compare/v0.5.4-20211018...v0.5.5-20211020
[0.5.4]: https://github.com/gahjelle/pyconfs/compare/v0.5.3-20211016...v0.5.4-20211018
[0.5.3]: https://github.com/gahjelle/pyconfs/compare/v0.5.2-20210608...v0.5.3-20211016
[0.5.2]: https://github.com/gahjelle/pyconfs/compare/v0.5.1-20201128...v0.5.2-20210608
[0.5.1]: https://github.com/gahjelle/pyconfs/compare/v0.5.0-20200622...v0.5.1-20201128
[0.5.0]: https://github.com/gahjelle/pyconfs/compare/v0.4.2-20200428...v0.5.0-20200622
[0.4.2]: https://github.com/gahjelle/pyconfs/compare/v0.4.1-20200420...v0.4.2-20200428
[0.4.1]: https://github.com/gahjelle/pyconfs/compare/v0.4.0-20200418...v0.4.1-20200420
[0.4.0]: https://github.com/gahjelle/pyconfs/compare/v0.3.3-20200405...v0.4.0-20200418
[0.3.3]: https://github.com/gahjelle/pyconfs/compare/v0.3.2-20200219...v0.3.3-20200405
[0.3.2]: https://github.com/gahjelle/pyconfs/compare/v0.3.1...v0.3.2-20200219
[0.3.1]: https://github.com/gahjelle/pyconfs/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/gahjelle/pyconfs/compare/v0.2.1...v0.3.0
[0.2.1]: https://github.com/gahjelle/pyconfs/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/gahjelle/pyconfs/compare/v0.1.4...v0.2.0
[0.1.4]: https://github.com/gahjelle/pyconfs/compare/v0.1.3...v0.1.4
[0.1.3]: https://github.com/gahjelle/pyconfs/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/gahjelle/pyconfs/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/gahjelle/pyconfs/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/gahjelle/pyconfs/releases/tag/v0.1.0

[#20]: https://github.com/gahjelle/pyconfs/pull/20
[#19]: https://github.com/gahjelle/pyconfs/pull/19
[#18]: https://github.com/gahjelle/pyconfs/pull/18
[#17]: https://github.com/gahjelle/pyconfs/pull/17
[#16]: https://github.com/gahjelle/pyconfs/pull/16
[#13]: https://github.com/gahjelle/pyconfs/pull/13
[#12]: https://github.com/gahjelle/pyconfs/pull/12
[#11]: https://github.com/gahjelle/pyconfs/pull/11
[#9]: https://github.com/gahjelle/pyconfs/pull/9
[#8]: https://github.com/gahjelle/pyconfs/pull/8
[#7]: https://github.com/gahjelle/pyconfs/pull/7
[#4]: https://github.com/gahjelle/pyconfs/pull/4
[#3]: https://github.com/gahjelle/pyconfs/pull/3
[#1]: https://github.com/gahjelle/pyconfs/pull/1
