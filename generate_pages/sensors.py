"""D-Bus sensor discovery via ksystemstats.

Discovers all available hardware sensors (CPU, memory, disk, network,
GPU, lm-sensors, etc.) and groups them by functional category for
use by page generators.

Requires PyGObject (gi). If missing, raises a clear error with
installation instructions.
"""

import re
import time
from collections import defaultdict

DEST = "org.kde.ksystemstats1"
PATH = "/org/kde/ksystemstats1"
IFACE = "org.kde.ksystemstats1"


def _check_gi():
    """Import gi, raising a helpful error if PyGObject is missing."""
    try:
        import gi
        gi.require_version("Gio", "2.0")
        from gi.repository import Gio, GLib  # noqa: E402
        return Gio, GLib
    except ImportError:
        raise SystemExit(
            "PyGObject (gi) is required but not installed.\n"
            "\n"
            "Install it with your system package manager:\n"
            "  Debian/Ubuntu:  sudo apt install python3-gi gir1.2-glib\n"
            "  Fedora:         sudo dnf install python3-gobject glib2\n"
            "  Arch:           sudo pacman -S python-gobject glib2\n"
            "  openSUSE:       sudo zypper install python3-gobject\n"
            "\n"
            "Then re-run this command."
        )


def discover_sensors():
    """Return a sorted list of all sensor IDs from ksystemstats.

    Calls the allSensors method over D-Bus and extracts the keys
    from the returned {id: metadata} dictionary.
    """
    Gio, GLib = _check_gi()
    conn = Gio.bus_get_sync(Gio.BusType.SESSION, None)
    r = conn.call_sync(
        DEST,
        PATH,
        IFACE,
        "allSensors",
        None,
        GLib.VariantType("(a{s(sssuidd)})"),
        Gio.DBusCallFlags.NONE,
        -1,
        None,
    )
    return sorted(r.get_child_value(0).unpack().keys())


def fetch_values(ids):
    """Fetch current values for a list of sensor IDs.

    Subscribes to the sensors, waits for data to accumulate,
    reads values in chunks of 50, then unsubscribes.

    Args:
        ids: List of sensor ID strings.

    Returns:
        Dict mapping sensor_id to its current value.
    """
    if not ids:
        return {}
    Gio, GLib = _check_gi()
    conn = Gio.bus_get_sync(Gio.BusType.SESSION, None)
    conn.call_sync(
        DEST,
        PATH,
        IFACE,
        "subscribe",
        GLib.Variant("(as)", (ids,)),
        None,
        Gio.DBusCallFlags.NONE,
        -1,
        None,
    )
    time.sleep(2)
    results = {}
    for i in range(0, len(ids), 50):
        chunk = ids[i : i + 50]
        r = conn.call_sync(
            DEST,
            PATH,
            IFACE,
            "sensorData",
            GLib.Variant("(as)", (chunk,)),
            GLib.VariantType("(a(sv))"),
            Gio.DBusCallFlags.NONE,
            -1,
            None,
        )
        for sid, val in r.get_child_value(0).unpack():
            results[sid] = val
    conn.call_sync(
        DEST,
        PATH,
        IFACE,
        "unsubscribe",
        GLib.Variant("(as)", (ids,)),
        None,
        Gio.DBusCallFlags.NONE,
        -1,
        None,
    )
    return results


def group_sensors(ids):
    """Group sensor IDs by functional category.

    Categories:
        cpu_cores: Per-core CPU sensors (usage, frequency, temperature)
        cpu_all: Aggregate CPU sensors (all/usage, all/averageFrequency, etc.)
        memory: Physical memory sensors
        swap: Swap memory sensors
        disk_all: Aggregate disk sensors
        disk_per: Per-disk sensors (keyed by disk UUID)
        net_all: Aggregate network sensors
        net_per: Per-interface network sensors (keyed by interface name)
        gpu: GPU sensors (keyed by gpu_id, then metric)
        lmsensors: lm-sensors hardware sensors
        power: Power supply sensors
        os: OS-level sensors

    Args:
        ids: List of sensor ID strings.

    Returns:
        Dict with category keys and sensor data as values.
    """
    g = {
        "cpu_cores": [],
        "cpu_all": {},
        "memory": {},
        "swap": {},
        "disk_all": {},
        "disk_per": defaultdict(set),
        "net_all": {},
        "net_per": defaultdict(set),
        "gpu": defaultdict(dict),
        "lmsensors": {},
        "power": {},
        "os": {},
    }
    for sid in ids:
        if re.match(r"cpu/cpu\d+/", sid):
            g["cpu_cores"].append(sid)
        elif sid.startswith("cpu/all/"):
            g["cpu_all"][sid] = True
        elif sid.startswith("memory/physical/"):
            g["memory"][sid] = True
        elif sid.startswith("memory/swap/"):
            g["swap"][sid] = True
        elif re.match(r"disk/(?!all)[^/]+/", sid):
            g["disk_per"][sid.split("/")[1]].add(sid)
        elif sid.startswith("disk/all/"):
            g["disk_all"][sid] = True
        elif re.match(r"network/(?!all)[^/]+/", sid):
            g["net_per"][sid.split("/")[1]].add(sid)
        elif sid.startswith("network/all/"):
            g["net_all"][sid] = True
        elif m := re.match(r"gpu/(gpu\d+)/(.+)", sid):
            g["gpu"][m.group(1)][m.group(2)] = sid
        elif sid.startswith("lmsensors/"):
            g["lmsensors"][sid] = True
        elif sid.startswith("power/"):
            g["power"][sid] = True
        elif sid.startswith("os/"):
            g["os"][sid] = True

    g["cpu_cores"] = sorted(
        set(g["cpu_cores"]),
        key=lambda x: int(re.search(r"(\d+)", x).group(1)),
    )
    return g
