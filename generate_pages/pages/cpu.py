"""CPU page generator.

Faces:
  2101 - Per-core usage (facegrid)
  2102 - Per-core frequency (linechart, max 6)
  2103 - Per-core temperature (facegrid)
  2104 - Per-core distribution (piechart)
  2105 - Overview (textonly)
"""

import math
import re

from ..blocks import (
    blk_appearance,
    blk_colors,
    blk_facegrid,
    blk_labels,
    blk_linechart,
    blk_page,
    blk_piechart,
    blk_row,
    blk_sensors,
    blk_textonly,
    blk_title_row,
)
from ..constants import COLOR_CPU_FREQ, COLOR_CPU_TOTAL, COLOR_FACEGRID_FALLBACK, RGB, palette_color
from ..i18n import t
from ..kconfig import kk, kp
from ..sensors import SensorGroups


def _sorted_cores(cores: list[str], suffix: str) -> list[str]:
    """Filter and sort per-core sensors by suffix.

    Example:
        _sorted_cores(["cpu/cpu0/usage", "cpu/cpu1/usage"], "/usage")
        -> ["cpu/cpu0/usage", "cpu/cpu1/usage"]
    """
    filtered = [s for s in cores if s.endswith(suffix)]
    return sorted(filtered, key=lambda x: int(re.search(r"(\d+)", x).group(1)))  # type: ignore[union-attr]


def generate(groups: SensorGroups, lang: str = "fr") -> str | None:
    """Generate CPU.page.

    Args:
        groups: Dict returned by group_sensors().
        lang: Language code ("fr" or "en").

    Returns:
        .page file content, or None if no CPU sensors available.
    """
    cores = groups["cpu_cores"]
    cpu_all = groups["cpu_all"]
    if not cores:
        return None

    P: list[str] = []
    P.append(blk_page("page.cpu", "cpu", lang))
    P.append(blk_title_row("page.cpu", lang))

    # --- Face 1: per-core usage (facegrid) ---
    cu = _sorted_cores(cores, "/usage")
    if cu:
        cc: dict[str, RGB] = {s: palette_color(i) for i, s in enumerate(cu)}
        cl = {s: f"{t('sensor.cpu.core', lang=lang)} {i + 1}" for i, s in enumerate(cu)}
        ncols = max(1, int(math.sqrt(len(cu)) + 0.999))

        P.append(blk_appearance(2101, "org.kde.ksysguard.facegrid", "face.cpu.per_core", lang))
        P.append(blk_sensors(2101, [kp(r"cpu/cpu\d+/usage")]))
        P.append(blk_colors(2101, {kk(r"cpu/cpu\d+/usage"): COLOR_FACEGRID_FALLBACK, **cc}))
        P.append(blk_labels(2101, cl))
        P.append(blk_facegrid(2101, ncols))

    # --- Face 2: frequency (linechart, max 6 lines) ---
    fr = _sorted_cores(cores, "/frequency")
    if fr:
        fc: dict[str, RGB] = {s: COLOR_CPU_FREQ for s in fr}
        fl = {s: f"{t('sensor.cpu.core', lang=lang)} {i + 1}" for i, s in enumerate(fr)}
        P.append(blk_appearance(2102, "org.kde.ksysguard.linechart", "face.cpu.freq_mhz", lang))
        P.append(blk_sensors(2102, fr[:6]))
        P.append(blk_colors(2102, fc))
        P.append(blk_labels(2102, fl))
        P.append(blk_linechart(2102, lineChartFillOpacity=15, showLegend="false"))

    # --- Face 3: per-core temperatures (facegrid) ---
    ct = _sorted_cores(cores, "/temperature")
    if ct:
        tc: dict[str, RGB] = {s: palette_color(i) for i, s in enumerate(ct)}
        tl = {s: f"{t('sensor.cpu.core', lang=lang)} {i + 1}" for i, s in enumerate(ct)}
        ncols = max(1, int(math.sqrt(len(ct)) + 0.999))
        P.append(blk_appearance(2103, "org.kde.ksysguard.facegrid", "face.cpu.per_core", lang))
        P.append(blk_sensors(2103, [kp(r"cpu/cpu\d+/temperature")]))
        P.append(blk_colors(2103, {kk(r"cpu/cpu\d+/temperature"): COLOR_FACEGRID_FALLBACK, **tc}))
        P.append(blk_labels(2103, tl))
        P.append(blk_facegrid(2103, ncols))

    # --- Face 4: distribution (piechart) ---
    if cu:
        P.append(blk_appearance(2104, "org.kde.ksysguard.piechart", "face.cpu.breakdown", lang))
        P.append(blk_sensors(2104, cu[:12]))
        P.append(blk_colors(2104, cc))
        P.append(blk_labels(2104, cl))
        P.append(blk_piechart(2104))

    # --- Face 5: overview (textonly) ---
    ti: list[str] = []
    for k in ["cpu/all/usage", "cpu/all/maximumUsage", "cpu/all/averageFrequency"]:
        if k in cpu_all:
            ti.append(k)
    if not ti:
        ti = ["cpu/all/usage"]
    P.append(blk_appearance(2105, "org.kde.ksysguard.textonly", "face.cpu.overview", lang))
    P.append(blk_sensors(2105, ti))
    P.append(blk_colors(2105, {s: COLOR_CPU_TOTAL for s in ti}))
    overview_labels = {
        "cpu/all/usage": t("sensor.cpu.overview.usage", lang=lang),
        "cpu/all/maximumUsage": t("sensor.cpu.overview.peak", lang=lang),
        "cpu/all/averageFrequency": t("sensor.cpu.overview.freq", lang=lang),
    }
    P.append(blk_labels(2105, {s: overview_labels.get(s, s) for s in ti}))
    P.append(blk_textonly(2105))

    # --- Layout ---
    P.append(blk_row(1, [2101, 2102]))
    if ct:
        P.append(blk_row(2, [2103, 2104]))
    P.append(blk_row(3, [2105]))

    return "\n".join(P) + "\n"
