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


def main() -> None:
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

    generated: list[str] = []
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
