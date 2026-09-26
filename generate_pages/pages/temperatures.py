"""Temperature page generator.

Faces:
  2601 - CPU + GPU (linechart)
  2602 - lm-sensors (linechart)
  2603 - Per-core temperature (facegrid)
  2604 - Current values (textonly)
  2605 - Fans (textonly)
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
    blk_row,
    blk_sensors,
    blk_textonly,
    blk_title_row,
)
from ..constants import palette_color
from ..i18n import t
from ..kconfig import kk, kp


def generate(groups, lang="fr"):
    """Generate Temperatures.page.

    Args:
        groups: Dict returned by group_sensors().
        lang: Language code ("fr" or "en").

    Returns:
        .page file content, or None if no sensors available.
    """
    lm = groups["lmsensors"]
    cpu_all = groups["cpu_all"]
    cores = groups["cpu_cores"]
    if not lm and not cpu_all:
        return None

    P = []
    P.append(blk_page("page.temperatures", "hwinfo", lang))
    P.append(blk_title_row("page.temperatures", lang))

    # --- CPU + GPU (linechart) ---
    t2601 = ["cpu/all/averageTemperature", "cpu/all/maximumTemperature"]
    for g in ["gpu1", "gpu0"]:
        if "temperature" in groups["gpu"].get(g, {}):
            t2601.append(f"gpu/{g}/temperature")
            break
    P.append(blk_appearance(2601, "org.kde.ksysguard.linechart", "face.temp.cpu_gpu", lang))
    P.append(blk_sensors(2601, t2601))
    P.append(
        blk_colors(
            2601,
            {
                "cpu/all/averageTemperature": (41, 128, 185),
                "cpu/all/maximumTemperature": (192, 57, 43),
                "gpu/gpu1/temperature": (39, 174, 96),
                "gpu/gpu0/temperature": (39, 174, 96),
            },
        )
    )
    P.append(
        blk_labels(
            2601,
            {
                "cpu/all/averageTemperature": t("sensor.temp.cpu_avg", lang=lang),
                "cpu/all/maximumTemperature": t("sensor.temp.cpu_max", lang=lang),
                "gpu/gpu1/temperature": t("sensor.temp.gpu", lang=lang),
                "gpu/gpu0/temperature": t("sensor.temp.gpu", lang=lang),
            },
        )
    )
    P.append(
        blk_linechart(
            2601, rangeAutoY="false", rangeFromY=20, rangeToY=110, lineChartFillOpacity=15
        )
    )

    # --- lm-sensors (linechart) ---
    lm_sorted = sorted(lm.keys())
    if lm_sorted:
        lm_colors = {}
        lm_labels = {}
        for i, s in enumerate(lm_sorted):
            lm_colors[s] = palette_color(i)
            chip = s.split("/")[1] if "/" in s else s
            feat = s.split("/")[-1] if "/" in s else s
            lm_labels[s] = f"{chip} {feat}"
        P.append(blk_appearance(2602, "org.kde.ksysguard.linechart", "face.temp.sensors", lang))
        P.append(blk_sensors(2602, lm_sorted))
        P.append(blk_colors(2602, lm_colors))
        P.append(blk_labels(2602, lm_labels))
        P.append(
            blk_linechart(
                2602, rangeAutoY="false", rangeFromY=20, rangeToY=110, lineChartFillOpacity=15
            )
        )

    # --- Per-core temperature (facegrid) ---
    ct = sorted(
        set(s for s in cores if s.endswith("/temperature")),
        key=lambda x: int(re.search(r"(\d+)", x).group(1)),
    )
    if ct:
        tc = {s: palette_color(i) for i, s in enumerate(ct)}
        tl = {s: f"{t('sensor.temp.core', lang=lang)} {i + 1}" for i, s in enumerate(ct)}
        ncols = max(1, int(math.sqrt(len(ct)) + 0.999))
        P.append(blk_appearance(2603, "org.kde.ksysguard.facegrid", "face.temp.per_core", lang))
        P.append(blk_sensors(2603, [kp(r"cpu/cpu\d+/temperature")]))
        P.append(blk_colors(2603, {kk(r"cpu/cpu\d+/temperature"): (95, 61, 233), **tc}))
        P.append(blk_labels(2603, tl))
        P.append(blk_facegrid(2603, ncols))

    # --- Current values (textonly) ---
    vi = [s for s in ["cpu/all/averageTemperature", "cpu/all/maximumTemperature"] if s in cpu_all]
    for g in sorted(groups["gpu"].keys()):
        if "temperature" in groups["gpu"][g]:
            vi.append(f"gpu/{g}/temperature")
    for s in lm_sorted[:3]:
        vi.append(s)
    if vi:
        current_labels = {
            "cpu/all/averageTemperature": t("sensor.cpu.total", lang=lang),
            "cpu/all/maximumTemperature": t("sensor.cpu.max_freq", lang=lang),
            "gpu/gpu1/temperature": t("sensor.temp.gpu", lang=lang),
            "gpu/gpu0/temperature": t("sensor.temp.gpu", lang=lang),
        }
        P.append(blk_appearance(2604, "org.kde.ksysguard.textonly", "face.temp.current", lang))
        P.append(blk_sensors(2604, vi))
        P.append(blk_colors(2604, {s: (41, 128, 185) for s in vi}))
        P.append(blk_labels(2604, {s: current_labels.get(s, s.split("/")[-1]) for s in vi}))
        P.append(blk_textonly(2604))

    # --- Fans (textonly) ---
    fans = sorted([s for s in lm if "fan" in s.lower()])
    if fans:
        P.append(blk_appearance(2605, "org.kde.ksysguard.textonly", "face.temp.fans", lang))
        P.append(blk_sensors(2605, fans))
        P.append(blk_colors(2605, {s: (41, 128, 185) for s in fans}))
        P.append(blk_labels(2605, {s: s.split("/")[-1] for s in fans}))
        P.append(blk_textonly(2605))

    # --- Layout ---
    P.append(blk_row(1, [2601, 2602] if lm_sorted else [2601]))
    rows2 = []
    if ct:
        rows2.append(2603)
    if vi:
        rows2.append(2604)
    if rows2:
        P.append(blk_row(2, rows2))
    if fans:
        P.append(blk_row(3, [2605]))

    return "\n".join(P) + "\n"
