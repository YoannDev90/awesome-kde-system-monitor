# Contributing

## Development Setup

```bash
# Install PyGObject (for D-Bus sensor access)
# Debian/Ubuntu:
sudo apt install python3-gi gir1.2-glib

# Fedora:
sudo dnf install python3-gobject glib2

# Arch:
sudo pacman -S python-gobject
```

## Testing Changes

1. Run the generator with your system's sensors:
   ```bash
   python3 -m generate_pages -o ./test-output -v
   ```

2. Test with English labels:
   ```bash
   python3 -m generate_pages -l en -o ./test-output-en -v
   ```

3. Copy generated files to your system and check in Plasma System Monitor:
   ```bash
   cp ./test-output/*.page ~/.local/share/plasma-systemmonitor/
   ```

4. Restart System Monitor to see changes.

## Code Conventions

- All user-facing strings go through `t("key", lang=lang)` — never hardcode French or English
- Face IDs are 5-digit numbers: 21xx (CPU), 22xx (Memory), 23xx (Disks), 24xx (Network), 25xx (GPU), 26xx (Temperatures)
- Colors use `(R, G, B)` tuples, converted to `R,G,B` strings by `constants.rgb()`
- Sensor regex escaping: `kp()` for `highPrioritySensorIds` (4 backslashes), `kk()` for keys (2 backslashes)
- All page generators have signature `generate(groups, lang="fr")`
- `blk_page()`, `blk_title_row()`, `blk_appearance()` accept a `lang` parameter
- Return `None` from a generator to skip that page (graceful degradation)

## Adding a New Page

1. Create `generate_pages/pages/yourpage.py` with a `generate(groups, lang="fr")` function
2. Use `t("key", lang=lang)` for all user-facing strings
3. Add translation keys to both `i18n/fr.json` and `i18n/en.json`
4. Return `None` if required sensors are missing
5. Register in `generate_pages/pages/__init__.py` `GENERATORS` dict
6. Add a `[page]` section with `icon`, `loadType=ondemand`, `version=1`
7. Pre-generate a reference `.page` file and commit it

## Adding a Language

1. Create `generate_pages/i18n/{lang}.json` (copy `fr.json` as template)
2. Add `"lang"` to the `choices` list in `__main__.py` `argparse`
3. Add language name to `--lang` help text
4. Test: `python3 -m generate_pages -l {lang} -v -o ./test-{lang}`

## Adding Sensors to an Existing Page

1. Open the relevant generator in `generate_pages/pages/`
2. Add sensor IDs to the appropriate face's `highPrioritySensorIds`
3. Add corresponding colors and labels (use `t()` for labels)
4. Add new translation keys if needed
5. Regenerate and test

## Commit Messages

Use concise, descriptive messages. Prefix with area when relevant:

- `cpu: add frequency graph`
- `i18n: add Portuguese translations`
- `memory: fix swap label`
- `docs: update README`
