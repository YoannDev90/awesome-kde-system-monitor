"""Memory page generator.

Faces:
  2201 - Physical usage (%)
  2202 - Volumes (textonly)
  2203 - Swap (%)
  2204 - Swap volumes (textonly)
"""

from ..blocks import (
    blk_appearance,
    blk_colors,
    blk_labels,
    blk_linechart,
    blk_page,
    blk_row,
    blk_sensors,
    blk_textonly,
    blk_title_row,
)
from ..i18n import t
from ..sensors import SensorGroups


def generate(groups: SensorGroups, lang: str = "fr") -> str | None:
    """Generate Memoire.page.

    Args:
        groups: Dict returned by group_sensors().
        lang: Language code ("fr" or "en").

    Returns:
        .page file content, or None if no memory sensors available.
    """
    mem = groups["memory"]
    swp = groups["swap"]
    if not mem:
        return None

    P: list[str] = []
    P.append(blk_page("page.memory", "memory", lang))
    P.append(blk_title_row("page.memory", lang))

    # --- Physical usage (%) ---
    P.append(blk_appearance(2201, "org.kde.ksysguard.linechart", "face.memory.usage_pct", lang))
    P.append(blk_sensors(2201, ["memory/physical/usedPercent"]))
    P.append(blk_colors(2201, {"memory/physical/usedPercent": (233, 61, 142)}))
    P.append(blk_labels(2201, {"memory/physical/usedPercent": t("sensor.mem.used", lang=lang)}))
    P.append(
        blk_linechart(2201, rangeAutoY="false", rangeFromY=0, rangeToY=100, lineChartFillOpacity=25)
    )

    # --- Volumes (textonly) ---
    vi = [
        s
        for s in ["memory/physical/used", "memory/physical/free", "memory/physical/total"]
        if s in mem
    ]
    if vi:
        P.append(blk_appearance(2202, "org.kde.ksysguard.textonly", "face.memory.volumes", lang))
        P.append(blk_sensors(2202, vi))
        P.append(blk_colors(2202, {s: (233, 61, 142) for s in vi}))
        vol_labels = {
            "memory/physical/used": t("sensor.mem.used", lang=lang),
            "memory/physical/free": t("sensor.mem.free", lang=lang),
            "memory/physical/total": t("sensor.mem.total", lang=lang),
        }
        P.append(blk_labels(2202, {s: vol_labels.get(s, s) for s in vi}))
        P.append(blk_textonly(2202))

    # --- Swap (%) ---
    if swp:
        P.append(blk_appearance(2203, "org.kde.ksysguard.linechart", "face.memory.swap_pct", lang))
        P.append(blk_sensors(2203, ["memory/swap/usedPercent"]))
        P.append(blk_colors(2203, {"memory/swap/usedPercent": (142, 68, 173)}))
        P.append(
            blk_labels(2203, {"memory/swap/usedPercent": t("sensor.mem.swap_used", lang=lang)})
        )
        P.append(
            blk_linechart(
                2203, rangeAutoY="false", rangeFromY=0, rangeToY=100, lineChartFillOpacity=20
            )
        )

    # --- Swap volumes (textonly) ---
    if swp:
        sv = [s for s in ["memory/swap/used", "memory/swap/free", "memory/swap/total"] if s in swp]
        if sv:
            P.append(
                blk_appearance(2204, "org.kde.ksysguard.textonly", "face.memory.swap_volumes", lang)
            )
            P.append(blk_sensors(2204, sv))
            P.append(blk_colors(2204, {s: (142, 68, 173) for s in sv}))
            swap_labels = {
                "memory/swap/used": t("sensor.mem.swap_used", lang=lang),
                "memory/swap/free": t("sensor.mem.free", lang=lang),
                "memory/swap/total": t("sensor.mem.swap_total", lang=lang),
            }
            P.append(blk_labels(2204, {s: swap_labels.get(s, s) for s in sv}))
            P.append(blk_textonly(2204))

    # --- Layout ---
    if swp:
        P.append(blk_row(1, [2201, 2202]))
        P.append(blk_row(2, [2203, 2204]))
    else:
        P.append(blk_row(1, [2201, 2202]))

    return "\n".join(P) + "\n"
