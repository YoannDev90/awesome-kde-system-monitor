"""Color palette and shared constants.

Loads a 64-color palette from palette.json and provides utilities
for color cycling and RGB formatting.
"""

import json
import os

# --- Palette from palette.json ---

_PALETTE_FILE = os.path.join(os.path.dirname(__file__), "palette.json")

with open(_PALETTE_FILE) as _f:
    _raw = json.load(_f)

# List of (R, G, B) tuples — 64 colors
PALETTE = [tuple(c) for c in _raw]


def palette_color(index):
    """Return the color at the given index (auto-cycles)."""
    return PALETTE[index % len(PALETTE)]


# --- AllInOne face IDs (fixed, for compatibility) ---

AIO_FACES = {
    "cpu": 94053970696496,
    "mem": 94054146401872,
    "gpu": 94333476531424,
    "gpu_detail": 94333478684288,
    "disk": 94054118236560,
    "net": 94476499300480,
    "temp": 94053970295360,
    "os": 94615221328912,
}


# --- Utilities ---


def rgb(t):
    """Convert an (R, G, B) tuple to an 'R,G,B' string."""
    return f"{t[0]},{t[1]},{t[2]}"
