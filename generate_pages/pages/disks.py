"""Disk page generator.

Faces:
  2301 - I/O activity (linechart)
  2302 - Per-disk usage (horizontalbars)
  2303 - Global disk space (linechart)
"""

from ..blocks import (
    blk_appearance,
    blk_colors,
    blk_labels,
    blk_linechart,
    blk_page,
    blk_row,
    blk_sensors,
    blk_title_row,
)
from ..constants import COLOR_READ, COLOR_USED, COLOR_WRITE
from ..i18n import t
from ..sensors import SensorGroups


def generate(groups: SensorGroups, lang: str = "fr") -> str | None:
    """Generate Disques.page.

    Args:
        groups: Dict returned by group_sensors().
        lang: Language code ("fr" or "en").

    Returns:
        .page file content, or None if no disk sensors available.
    """
    dp = groups["disk_per"]
    da = groups["disk_all"]
    if not dp and not da:
        return None

    P: list[str] = []
    P.append(blk_page("page.disks", "drive-harddisk", lang))
    P.append(blk_title_row("page.disks", lang))

    # --- Read/write activity ---
    P.append(blk_appearance(2301, "org.kde.ksysguard.linechart",
                            "face.disks.activity", lang))
    P.append(blk_sensors(2301, ["disk/all/read", "disk/all/write"]))
    P.append(blk_colors(2301, {
        "disk/all/read": COLOR_READ,
        "disk/all/write": COLOR_WRITE,
    }))
    P.append(blk_labels(2301, {
        "disk/all/read": t("sensor.disk.read", lang=lang),
        "disk/all/write": t("sensor.disk.write", lang=lang),
    }))
    P.append(blk_linechart(2301, lineChartFillOpacity=15))

    # --- Per-disk usage (horizontalbars) ---
    dids = sorted(dp.keys())
    used_dids = [d for d in dids if f"disk/{d}/used" in dp[d]]
    if used_dids:
        ui = [f"disk/{d}/used" for d in used_dids]
        P.append(blk_appearance(2302, "org.kde.ksysguard.horizontalbars",
                                "face.disks.used_space", lang))
        P.append(blk_sensors(2302, ui))
        P.append(blk_colors(2302, {s: COLOR_USED for s in ui}))
        P.append(blk_labels(2302, {s: d[:12] for s, d in zip(ui, used_dids)}))

    # --- Global disk space ---
    P.append(blk_appearance(2303, "org.kde.ksysguard.linechart",
                            "face.disks.disk_space", lang))
    P.append(blk_sensors(2303, ["disk/all/used"]))
    P.append(blk_colors(2303, {"disk/all/used": COLOR_USED}))
    P.append(blk_labels(2303, {"disk/all/used": t("sensor.mem.used", lang=lang)}))
    P.append(blk_linechart(2303, lineChartFillOpacity=20))

    # --- Layout ---
    if used_dids:
        P.append(blk_row(1, [2301, 2302]))
    else:
        P.append(blk_row(1, [2301]))
    P.append(blk_row(2, [2303]))

    return "\n".join(P) + "\n"
