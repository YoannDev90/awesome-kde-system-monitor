"""OS page generator.

Faces:
  2801 - System info (textonly)
"""

from ..blocks import (
    blk_appearance,
    blk_colors,
    blk_labels,
    blk_page,
    blk_row,
    blk_sensors,
    blk_textonly,
    blk_title_row,
)
from ..constants import COLOR_PRIMARY
from ..sensors import SensorGroups


def generate(groups: SensorGroups, lang: str = "fr") -> str | None:
    """Generate Systeme.page.

    Args:
        groups: Dict returned by group_sensors().
        lang: Language code ("fr" or "en").

    Returns:
        .page file content, or None if no OS sensors available.
    """
    os = groups["os"]
    if not os:
        return None

    P: list[str] = []
    P.append(blk_page("page.os", "computer", lang))
    P.append(blk_title_row("page.os", lang))

    # --- System info (textonly) ---
    os_ids = sorted(os.keys())[:8]
    P.append(blk_appearance(2801, "org.kde.ksysguard.textonly",
                            "face.os.info", lang))
    P.append(blk_sensors(2801, os_ids))
    P.append(blk_colors(2801, {s: COLOR_PRIMARY for s in os_ids}))
    P.append(blk_labels(2801, {s: s.split("/")[-1] for s in os_ids}))
    P.append(blk_textonly(2801))

    # --- Layout ---
    P.append(blk_row(1, [2801]))

    return "\n".join(P) + "\n"
