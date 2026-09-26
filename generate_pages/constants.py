"""Color palette and shared constants.

Loads a 64-color palette from palette.json and provides utilities
for color cycling, RGB formatting, and named semantic colors.
"""

import json
import os
from typing import TypeAlias

# --- Palette from palette.json ---

_PALETTE_FILE = os.path.join(os.path.dirname(__file__), "palette.json")

with open(_PALETTE_FILE) as _f:
    _raw: list[list[int]] = json.load(_f)

# List of (R, G, B) tuples — 64 colors
PALETTE: list[tuple[int, int, int]] = [tuple(c) for c in _raw]  # type: ignore[misc]

# Type alias for RGB colors
RGB: TypeAlias = tuple[int, int, int]


def palette_color(index: int) -> RGB:
    """Return the color at the given index (auto-cycles)."""
    return PALETTE[index % len(PALETTE)]


# --- Semantic colors ---

# Network
COLOR_DOWNLOAD: RGB = (41, 128, 185)
COLOR_UPLOAD: RGB = (39, 174, 96)

# Disk
COLOR_READ: RGB = (41, 128, 185)
COLOR_WRITE: RGB = (233, 61, 142)

# Memory
COLOR_USED: RGB = (233, 61, 142)
COLOR_FREE: RGB = (39, 174, 96)
COLOR_CACHE: RGB = (127, 233, 61)
COLOR_BUFFER: RGB = (243, 156, 18)
COLOR_SWAP: RGB = (142, 68, 173)

# CPU
COLOR_CPU_TOTAL: RGB = (41, 128, 185)
COLOR_CPU_FREQ: RGB = (142, 68, 173)
COLOR_CPU_BREAKDOWN_SYS: RGB = (41, 128, 185)
COLOR_CPU_BREAKDOWN_USER: RGB = (39, 174, 96)
COLOR_CPU_BREAKDOWN_WAIT: RGB = (243, 156, 18)

# Temperature
COLOR_TEMP_AVG: RGB = (41, 128, 185)
COLOR_TEMP_MAX: RGB = (192, 57, 43)
COLOR_TEMP_GPU: RGB = (39, 174, 96)

# GPU
COLOR_DGPU: RGB = (127, 140, 141)
COLOR_IGPU: RGB = (41, 128, 185)
COLOR_VRAM: RGB = (61, 209, 233)

# Facegrid fallback
COLOR_FACEGRID_FALLBACK: RGB = (95, 61, 233)

# Generic
COLOR_PRIMARY: RGB = (41, 128, 185)
COLOR_SECONDARY: RGB = (142, 68, 173)
COLOR_ACCENT: RGB = (39, 174, 96)
COLOR_WARNING: RGB = (243, 156, 18)
COLOR_NEUTRAL: RGB = (127, 140, 141)


# --- AllInOne face IDs (fixed, for compatibility) ---

AIO_FACES: dict[str, int] = {
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

def rgb(t: RGB) -> str:
    """Convert an (R, G, B) tuple to an 'R,G,B' string."""
    return f"{t[0]},{t[1]},{t[2]}"
