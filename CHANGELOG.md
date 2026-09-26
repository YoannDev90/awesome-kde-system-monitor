# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Added
- Power page generator (battery/supply sensors)
- OS page generator (hostname, uptime, system info)
- Generated overview page (replaces static Page.page)
- CLI flags: `--live`, `--diff`, `--show-colors`, `--preview`, `--watch`
- Unit tests (67 tests: kconfig, i18n, sensors, blocks, all generators)
- Cross-validation in `--validate` (duplicate faces, orphan faces, unreferenced faces)
- Named semantic color constants (COLOR_DOWNLOAD, COLOR_USED, etc.)
- Type hints on all modules

### Changed
- i18n module: lazy JSON loading with cache, `lang` parameter on `t()`
- `blk_appearance`, `blk_page`, `blk_title_row` accept `lang` parameter
- All docstrings translated to English
- Deferred PyGObject import with clear install instructions

### Fixed
- `kp()` was identical to `kk()` (should produce 4 backslashes, not 2)
- Network page generator used wrong colors (green instead of blue)

## [1.0.0] - 2026-09-26

### Added
- Initial release
- 7 pre-generated `.page` files (CPU, Memory, Disks, Network, GPU, Temperatures, Overview)
- Python generator with D-Bus sensor discovery (ksystemstats)
- i18n module with fr/en translations
- KConfig block builders
- CLI entry point with `--list-sensors`, `--lang`, `--validate`, `--output-dir`
- MIT license
