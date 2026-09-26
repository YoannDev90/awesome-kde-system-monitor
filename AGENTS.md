# Repository Guidelines

## What This Repo Is

KDE Plasma System Monitor custom pages (`.page` files) and a Python generator (`generate_pages/`) that auto-adapts to detected hardware sensors.

## Key Files

- `*.page` — Pre-generated KConfig INI files for plasma-systemmonitor
- `generate_pages/__main__.py` — CLI entry point (`python3 -m generate_pages`)
- `generate_pages/sensors.py` — D-Bus sensor discovery via ksystemstats
- `generate_pages/blocks.py` — KConfig block builders (faces, layouts, charts)
- `generate_pages/kconfig.py` — Regex escaping helpers (`kp`/`kk`)
- `generate_pages/i18n/__init__.py` — Translation function `t(key, lang=)`
- `generate_pages/i18n/*.json` — Translation files (fr, en)
- `generate_pages/pages/*.py` — Per-category page generators

## Build / Run Commands

```bash
# List sensors
python3 -m generate_pages --list-sensors

# Generate all pages (French default)
python3 -m generate_pages -o .

# Generate with English labels
python3 -m generate_pages -l en -o .

# Generate + validate
python3 -m generate_pages -v
```

## Code Style

- Python 3.10+, no type hints used
- French-first bilingual strings: French default, English via `[en]` suffix
- Face IDs: 21xx CPU, 22xx Memory, 23xx Disks, 24xx Network, 25xx GPU, 26xx Temperatures
- KConfig backslash rules: `kp()` = 4 backslashes, `kk()` = 2 backslashes
- No external dependencies beyond PyGObject
- All user-facing strings go through i18n: `t("key", lang=lang)`

## Architecture

Generator pipeline:
1. `sensors.py:discover_sensors()` — D-Bus call to ksystemstats
2. `sensors.py:group_sensors()` — Categorize by type (cpu, memory, disk, net, gpu, lmsensors)
3. `pages/*.py:generate(groups, lang)` — Build KConfig blocks, return `.page` string
4. `__main__.py` — Write files, optionally validate regex patterns

i18n flow:
- `set_lang(lang)` loads `i18n/{lang}.json`
- `t("key", lang=lang)` returns translated string, falls back to key
- Generators pass `lang` to `blk_page()`, `blk_appearance()`, `blk_title_row()`, and inline `t()` calls for sensor labels

Each page generator returns `None` if required sensors are absent (graceful degradation).

## Testing

No test suite. Validate with:
```bash
python3 -m generate_pages -v -o ./test-output
python3 -m generate_pages -v -l en -o ./test-output-en
```
Then visually verify in Plasma System Monitor.
