"""CLI entry point: python3 -m generate_pages.

Discovers system sensors via D-Bus (ksystemstats), generates .page files
for plasma-systemmonitor, and optionally validates sensor patterns.
"""

import argparse
import difflib
import os
import re
import sys
import time

from .constants import PALETTE, rgb
from .i18n import set_lang
from .pages import GENERATORS
from .sensors import discover_sensors, fetch_values, group_sensors


def print_sensor_report(groups: dict) -> None:
    """Print a report of detected sensors, grouped by type."""
    for key in [
        "cpu_cores",
        "cpu_all",
        "memory",
        "swap",
        "disk_all",
        "disk_per",
        "net_all",
        "net_per",
        "gpu",
        "lmsensors",
        "power",
        "os",
    ]:
        val = groups[key]
        n = len(val) if not isinstance(val, set) else len(val)
        if n == 0:
            continue
        print(f"\n  {key} ({n}):")
        items = sorted(val.keys()) if isinstance(val, dict) else sorted(val)
        for s in items[:20]:
            print(f"    {s}")
        if n > 20:
            print(f"    ... and {n - 20} more")


def _show_colors() -> None:
    """Display the color palette in the terminal."""
    print("Color palette (64 colors):")
    for i, c in enumerate(PALETTE):
        r, g, b = c
        block = f"\033[48;2;{r};{g};{b}m  \033[0m"
        print(f"  {i:2d}: {block} {rgb(c)}")
    print()


def _preview(groups: dict, lang: str) -> None:
    """Show a summary of what would be generated."""
    print("Preview of generated pages:")
    for fname, gen_func in GENERATORS.items():
        content = gen_func(groups, lang=lang)
        if content:
            n_faces = len(re.findall(r"\[Face-\d+\]\[Appearance\]", content))
            n_rows = len(re.findall(r"\[page\]\[row-\d+\]", content))
            lines = content.count("\n")
            print(f"  {fname:24s}  {n_faces} faces, {n_rows} rows, {lines} lines")
        else:
            print(f"  {fname:24s}  (skipped — no sensors)")


def _diff(path: str, new_content: str) -> bool:
    """Show diff between existing file and new content. Returns True if different."""
    if not os.path.exists(path):
        print(f"  {os.path.basename(path)}: new file")
        return True
    with open(path) as f:
        old_lines = f.readlines()
    new_lines = new_content.splitlines(keepends=True)
    diff = list(difflib.unified_diff(
        old_lines, new_lines,
        fromfile=f"a/{os.path.basename(path)}",
        tofile=f"b/{os.path.basename(path)}",
    ))
    if not diff:
        return False
    for line in diff:
        if line.startswith("+++") or line.startswith("---"):
            print(line.rstrip())
        elif line.startswith("+"):
            print(f"\033[32m{line.rstrip()}\033[0m")
        elif line.startswith("-"):
            print(f"\033[31m{line.rstrip()}\033[0m")
        else:
            print(line.rstrip())
    return True


def _live(ids: list[str]) -> None:
    """Fetch and display live sensor values."""
    print("Fetching live sensor values...")
    values = fetch_values(ids)
    for sid in sorted(values):
        val = values[sid]
        print(f"  {sid}: {val}")


def _watch(groups: dict, lang: str, output_dir: str, interval: int) -> None:
    """Regenerate pages periodically."""
    print(f"Watching for changes (Ctrl+C to stop, interval={interval}s)...")
    try:
        while True:
            for fname, gen_func in GENERATORS.items():
                content = gen_func(groups, lang=lang)
                if content:
                    path = os.path.join(output_dir, fname)
                    with open(path, "w") as f:
                        f.write(content)
            sys.stdout.write(f"\r  Regenerated at {time.strftime('%H:%M:%S')}")
            sys.stdout.flush()
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n  Stopped watching.")


def main() -> None:
    """CLI entry point: discovery -> generation -> optional validation."""
    parser = argparse.ArgumentParser(
        description="Generate .page files for plasma-systemmonitor",
    )
    parser.add_argument(
        "-o", "--output-dir", default=".",
        help="Output directory (default: .)",
    )
    parser.add_argument(
        "-v", "--validate", action="store_true",
        help="Validate generated files",
    )
    parser.add_argument(
        "--list-sensors", action="store_true",
        help="List detected sensors and exit",
    )
    parser.add_argument(
        "-l", "--lang", default="fr", choices=["fr", "en"],
        help="Label language (default: fr)",
    )
    parser.add_argument(
        "--live", action="store_true",
        help="Fetch and display live sensor values",
    )
    parser.add_argument(
        "--diff", action="store_true",
        help="Show diff before overwriting existing files",
    )
    parser.add_argument(
        "--show-colors", action="store_true",
        help="Display the color palette and exit",
    )
    parser.add_argument(
        "--preview", action="store_true",
        help="Show summary of what would be generated",
    )
    parser.add_argument(
        "--watch", action="store_true",
        help="Regenerate pages every 30s (Ctrl+C to stop)",
    )
    parser.add_argument(
        "--interval", type=int, default=30,
        help="Watch interval in seconds (default: 30)",
    )
    args = parser.parse_args()

    if args.show_colors:
        _show_colors()
        return

    set_lang(args.lang)

    print("Discovering sensors...")
    ids = discover_sensors()
    print(f"  {len(ids)} sensors found")

    groups = group_sensors(ids)

    if args.list_sensors:
        print_sensor_report(groups)
        return

    if args.preview:
        _preview(groups, args.lang)
        return

    if args.live:
        _live(ids)
        return

    if args.watch:
        os.makedirs(args.output_dir, exist_ok=True)
        _watch(groups, args.lang, args.output_dir, args.interval)
        return

    os.makedirs(args.output_dir, exist_ok=True)

    generated: list[str] = []
    for fname, gen_func in GENERATORS.items():
        content = gen_func(groups, lang=args.lang)
        if content:
            path = os.path.join(args.output_dir, fname)
            if args.diff and os.path.exists(path):
                changed = _diff(path, content)
                if not changed:
                    print(f"  Unchanged: {fname}")
                    continue
            with open(path, "w") as f:
                f.write(content)
            print(f"  Generated: {fname}")
            generated.append(fname)
        else:
            print(f"  Skipped: {fname} (insufficient sensors)")

    if args.validate:
        print("\nValidation:")
        for fname in generated:
            path = os.path.join(args.output_dir, fname)
            problems = _validate_page(path, ids)
            status = "OK" if not problems else f"{len(problems)} issue(s)"
            print(f"  {fname}: {status}")
            for p in problems:
                print(f"    {p}")

    print(f"\nDone: {len(generated)} page(s) in {args.output_dir}")


def _validate_page(path: str, real_ids: list[str]) -> list[str]:
    """Validate a .page file with multiple checks.

    Checks:
        1. Sensor patterns match at least one real sensor
        2. No duplicate face IDs defined
        3. All face IDs referenced in layout are defined
        4. All defined faces are referenced in layout
    """
    real = set(real_ids)
    problems: list[str] = []
    with open(path) as f:
        content = f.read()

    # 1. Sensor pattern matching
    for m in re.finditer(r"highPrioritySensorIds=\[(.*?)\]", content):
        for token in re.findall(r'"([^"]+)"', m.group(1)):
            if any(c in token for c in ["\\", "*", "(", "["]):
                unescaped = (
                    token.replace("\\\\\\\\", "\x00")
                    .replace("\\\\", "\\")
                    .replace("\x00", "\\\\")
                )
                matched = False
                for rid in real:
                    try:
                        if re.fullmatch(unescaped, rid):
                            matched = True
                            break
                    except re.error:
                        matched = True
                        break
                if not matched:
                    problems.append(f"Unmatched pattern: {token}")
            else:
                if token not in real:
                    problems.append(f"Missing sensor: {token}")

    # 2. Duplicate face IDs
    defined_faces = re.findall(r"\[Face-(\d+)\]\[Appearance\]", content)
    seen: set[str] = set()
    for fid in defined_faces:
        if fid in seen:
            problems.append(f"Duplicate face ID: Face-{fid}")
        seen.add(fid)

    # 3. Referenced faces exist
    referenced_faces = re.findall(r"face=Face-(\d+)", content)
    for fid in referenced_faces:
        if fid not in defined_faces:
            problems.append(f"Referenced face not defined: Face-{fid}")

    # 4. Defined faces are referenced
    for fid in defined_faces:
        if fid not in referenced_faces:
            problems.append(f"Defined face not referenced: Face-{fid}")

    return problems


if __name__ == "__main__":
    main()
