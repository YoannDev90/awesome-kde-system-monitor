"""CLI entry point: python3 -m generate_pages.

Discovers system sensors via D-Bus (ksystemstats), generates .page files
for plasma-systemmonitor, and optionally validates sensor patterns.
"""

import argparse
import os
import re

from .i18n import set_lang
from .pages import GENERATORS
from .sensors import discover_sensors, group_sensors


def print_sensor_report(groups):
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


def main():
    """CLI entry point: discovery -> generation -> optional validation."""
    parser = argparse.ArgumentParser(
        description="Generate .page files for plasma-systemmonitor",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default=".",
        help="Output directory (default: .)",
    )
    parser.add_argument(
        "-v",
        "--validate",
        action="store_true",
        help="Validate generated files",
    )
    parser.add_argument(
        "--list-sensors",
        action="store_true",
        help="List detected sensors and exit",
    )
    parser.add_argument(
        "-l",
        "--lang",
        default="fr",
        choices=["fr", "en"],
        help="Label language (default: fr)",
    )
    args = parser.parse_args()

    set_lang(args.lang)

    print("Discovering sensors...")
    ids = discover_sensors()
    print(f"  {len(ids)} sensors found")

    groups = group_sensors(ids)

    if args.list_sensors:
        print_sensor_report(groups)
        return

    os.makedirs(args.output_dir, exist_ok=True)

    generated = []
    for fname, gen_func in GENERATORS.items():
        content = gen_func(groups, lang=args.lang)
        if content:
            path = os.path.join(args.output_dir, fname)
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


def _validate_page(path, real_ids):
    """Verify that all highPrioritySensorIds match at least one real sensor.

    Patterns containing regex characters (\\, *, (, [) are tested as regex.
    Literal IDs are looked up in the sensor set.
    """
    real = set(real_ids)
    problems = []
    with open(path) as f:
        content = f.read()
    for m in re.finditer(r"highPrioritySensorIds=\[(.*?)\]", content):
        for token in re.findall(r'"([^"]+)"', m.group(1)):
            if any(c in token for c in ["\\", "*", "(", "["]):
                unescaped = (
                    token.replace("\\\\\\\\", "\x00").replace("\\\\", "\\").replace("\x00", "\\\\")
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
    return problems


if __name__ == "__main__":
    main()
