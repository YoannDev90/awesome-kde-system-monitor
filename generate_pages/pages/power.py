"""Power page generator.

Faces:
  2701 - Battery charge (%)
  2702 - Power details (textonly)
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
from ..constants import COLOR_ACCENT, COLOR_USED, RGB
from ..sensors import SensorGroups


def generate(groups: SensorGroups, lang: str = "fr") -> str | None:
    """Generate Alimentation.page.

    Args:
        groups: Dict returned by group_sensors().
        lang: Language code ("fr" or "en").

    Returns:
        .page file content, or None if no power sensors available.
    """
    pw = groups["power"]
    if not pw:
        return None

    P: list[str] = []
    P.append(blk_page("page.power", "battery", lang))
    P.append(blk_title_row("page.power", lang))

    # --- Battery charge (%) ---
    charge_ids = [s for s in sorted(pw) if "charge" in s.lower() or "capacity" in s.lower()]
    if charge_ids:
        P.append(blk_appearance(2701, "org.kde.ksysguard.linechart",
                                "face.power.charge", lang))
        P.append(blk_sensors(2701, charge_ids[:4]))
        cols: dict[str, RGB] = {s: COLOR_ACCENT for s in charge_ids[:4]}
        P.append(blk_colors(2701, cols))
        P.append(blk_labels(2701, {s: s.split("/")[-1] for s in charge_ids[:4]}))
        P.append(blk_linechart(2701, rangeAutoY="false", rangeFromY=0,
                               rangeToY=100, lineChartFillOpacity=25))

    # --- Power details (textonly) ---
    detail_ids = [s for s in sorted(pw) if s not in charge_ids]
    if detail_ids:
        P.append(blk_appearance(2702, "org.kde.ksysguard.textonly",
                                "face.power.details", lang))
        P.append(blk_sensors(2702, detail_ids[:6]))
        P.append(blk_colors(2702, {s: COLOR_USED for s in detail_ids[:6]}))
        P.append(blk_labels(2702, {s: s.split("/")[-1] for s in detail_ids[:6]}))
        P.append(blk_textonly(2702))

    # --- Layout ---
    if charge_ids and detail_ids:
        P.append(blk_row(1, [2701, 2702]))
    elif charge_ids:
        P.append(blk_row(1, [2701]))
    elif detail_ids:
        P.append(blk_row(1, [2702]))

    return "\n".join(P) + "\n"
