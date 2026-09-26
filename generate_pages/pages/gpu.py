"""GPU page generator.

Faces:
  2501 - Usage (%)
  2502 - Video memory (VRAM)
  2503 - Frequency (MHz)
  2504 - Details (textonly)
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
from ..constants import RGB
from ..i18n import t
from ..sensors import SensorGroups

GPU_COLORS: dict[str, RGB] = {"gpu0": (127, 140, 141), "gpu1": (41, 128, 185)}
GPU_LABELS: dict[str, str] = {"gpu0": "sensor.gpu.dgpu", "gpu1": "sensor.gpu.igpu"}


def _gpu_col(gpu_id: str) -> RGB:
    """Return the default color for a GPU."""
    base = gpu_id.split("/")[0] if "/" in gpu_id else gpu_id
    return GPU_COLORS.get(base, (41, 128, 185))


def _gpu_label(gpu_id: str, metric: str = "", lang: str = "fr") -> str:
    """Return translated label for a GPU.

    Args:
        gpu_id: Full sensor ID (e.g. "gpu/gpu1/usage").
        metric: Optional suffix (e.g. "VRAM").
        lang: Language code.
    """
    base = gpu_id.split("/")[0] if "/" in gpu_id else gpu_id
    name_key = GPU_LABELS.get(base, base)
    name = t(name_key, lang=lang) if name_key.startswith("sensor.") else name_key
    return f"{name} {metric}" if metric else name


def generate(groups: SensorGroups, lang: str = "fr") -> str | None:
    """Generate GPU.page.

    Args:
        groups: Dict returned by group_sensors().
        lang: Language code ("fr" or "en").

    Returns:
        .page file content, or None if no GPU sensors available.
    """
    gpus = groups["gpu"]
    if not gpus:
        return None
    gnames = sorted(gpus.keys())
    P: list[str] = []
    P.append(blk_page("page.gpu", "video-display", lang))
    P.append(blk_title_row("page.gpu", lang))

    # --- Usage (%) ---
    fi = [f"gpu/{g}/usage" for g in gnames if "usage" in groups["gpu"][g]]
    if fi:
        P.append(blk_appearance(2501, "org.kde.ksysguard.linechart", "face.gpu.usage_pct", lang))
        P.append(blk_sensors(2501, fi))
        P.append(blk_colors(2501, {s: _gpu_col(s) for s in fi}))
        P.append(
            blk_labels(
                2501,
                {s: t(GPU_LABELS.get(s.split("/")[0], s.split("/")[0]), lang=lang) for s in fi},
            )
        )
        P.append(
            blk_linechart(
                2501, rangeAutoY="false", rangeFromY=0, rangeToY=100, lineChartFillOpacity=25
            )
        )

    # --- VRAM ---
    vi = [f"gpu/{g}/usedVram" for g in gnames if "usedVram" in groups["gpu"][g]]
    if vi:
        P.append(blk_appearance(2502, "org.kde.ksysguard.linechart", "face.gpu.vram", lang))
        P.append(blk_sensors(2502, vi))
        P.append(blk_colors(2502, {s: _gpu_col(s) for s in vi}))
        P.append(
            blk_labels(
                2502,
                {s: t(GPU_LABELS.get(s.split("/")[0], s.split("/")[0]), lang=lang) for s in vi},
            )
        )
        P.append(blk_linechart(2502, lineChartFillOpacity=20))

    # --- Frequencies ---
    fri: list[str] = []
    for g in gnames:
        for metric in ["coreFrequency", "memoryFrequency"]:
            if metric in groups["gpu"].get(g, {}):
                fri.append(f"gpu/{g}/{metric}")
    if fri:
        P.append(blk_appearance(2503, "org.kde.ksysguard.linechart", "face.gpu.freq_mhz", lang))
        P.append(blk_sensors(2503, fri))
        fcols: dict[str, RGB] = {
            "coreFrequency": (41, 128, 185),
            "memoryFrequency": (142, 68, 173),
        }
        P.append(blk_colors(2503, {s: fcols.get(s.split("/")[-1], (41, 128, 185)) for s in fri}))
        freq_labels = {
            "coreFrequency": t("sensor.gpu.core", lang=lang),
            "memoryFrequency": t("sensor.gpu.memory", lang=lang),
        }
        P.append(blk_labels(2503, {s: freq_labels.get(s.split("/")[-1], s) for s in fri}))
        P.append(blk_linechart(2503, lineChartFillOpacity=15))

    # --- Details (textonly) ---
    di: list[str] = []
    for g in gnames:
        for metric in ["usage", "totalVram", "temperature", "power"]:
            if metric in groups["gpu"].get(g, {}):
                di.append(f"gpu/{g}/{metric}")
    if di:
        detail_labels = {
            "usage": t("sensor.cpu.overview.usage", lang=lang),
            "totalVram": t("sensor.gpu.vram_label", lang=lang),
            "temperature": t("sensor.temp.gpu", lang=lang),
            "power": "Power",
        }
        P.append(blk_appearance(2504, "org.kde.ksysguard.textonly", "face.gpu.detail", lang))
        P.append(blk_sensors(2504, di))
        P.append(blk_colors(2504, {s: _gpu_col(s) for s in di}))
        P.append(
            blk_labels(
                2504, {s: _gpu_label(s, detail_labels.get(s.split("/")[-1], ""), lang) for s in di}
            )
        )
        P.append(blk_textonly(2504))

    # --- Layout ---
    rows: list[list[int]] = []
    if fi:
        row = [2501]
        if vi:
            row.append(2502)
        rows.append(row)
    if fri:
        row = [2503]
        if di:
            row.append(2504)
        rows.append(row)
    if not rows and di:
        rows.append([2504])
    for i, r in enumerate(rows, 1):
        P.append(blk_row(i, r))

    return "\n".join(P) + "\n"
