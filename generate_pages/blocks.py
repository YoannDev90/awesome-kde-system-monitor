"""KConfig block generators (.page files).

Provides functions to build INI sections for .page files:
- Faces: appearance, sensors, colors, labels, chart types
- Layout: page, title row, content rows
"""

from .constants import RGB, rgb
from .i18n import t

# --- Faces ---


def blk_appearance(
    fid: int,
    chart: str,
    title_key: str,
    lang: str = "fr",
    show_title: bool = True,
) -> str:
    """Build [Face-N][Appearance] block with bilingual title.

    Args:
        fid: Numeric face ID (e.g. 2101).
        chart: KSysGuard chart type (e.g. "org.kde.ksysguard.linechart").
        title_key: i18n key for the title (e.g. "face.cpu.total_usage").
        lang: Language code for the [en] suffix.
        show_title: Whether to show the title in the widget.
    """
    title_fr = t(title_key, lang=lang)
    title_en = t(title_key, lang="en")
    lines = [
        f"[Face-{fid}][Appearance]",
        f"chartFace={chart}",
        f"title={title_fr}",
        f"Title={title_fr}",
        f"title[en]={title_en}",
        f"Title[en]={title_en}",
    ]
    if not show_title:
        lines.append("showTitle=false")
    return "\n".join(lines) + "\n"


def blk_sensors(fid: int, high: list[str], low: list[str] | None = None) -> str:
    """Build [Face-N][Sensors] block with highPrioritySensorIds.

    Args:
        fid: Numeric face ID.
        high: List of sensor IDs or regex patterns.
        low: Low-priority sensor list (optional).
    """
    h = "[" + ",".join(f'"{s}"' for s in high) + "]"
    lo = "[]"
    return f"[Face-{fid}][Sensors]\nhighPrioritySensorIds={h}\nlowPrioritySensorIds={lo}\n"


def blk_colors(fid: int, cmap: dict[str, RGB]) -> str:
    """Build [Face-N][SensorColors] block with R,G,B values.

    Args:
        fid: Numeric face ID.
        cmap: Dict {sensor_id: (R, G, B)}.
    """
    lines = [f"[Face-{fid}][SensorColors]"]
    for sid, c in sorted(cmap.items()):
        lines.append(f"{sid}={rgb(c)}")
    return "\n".join(lines) + "\n"


def blk_labels(fid: int, lmap: dict[str, str]) -> str:
    """Build [Face-N][SensorLabels] block with per-sensor labels.

    Args:
        fid: Numeric face ID.
        lmap: Dict {sensor_id: label_string}.
    """
    lines = [f"[Face-{fid}][SensorLabels]"]
    for sid, lbl in sorted(lmap.items()):
        lines.append(f"{sid}={lbl}")
    return "\n".join(lines) + "\n"


def blk_linechart(fid: int, **kw: object) -> str:
    """Build [Face-N][org.kde.ksysguard.linechart][General] block.

    Defaults: historyAmount=300, lineChartFillOpacity=20,
    rangeAutoY=true, showLegend=true.

    Args:
        fid: Numeric face ID.
        **kw: Override parameters (e.g. rangeAutoY="false").
    """
    defaults: dict[str, object] = {
        "historyAmount": 300,
        "lineChartFillOpacity": 20,
        "rangeAutoY": "true",
        "showLegend": "true",
    }
    defaults.update(kw)
    lines = [f"[Face-{fid}][org.kde.ksysguard.linechart][General]"]
    for k, v in defaults.items():
        lines.append(f"{k}={v}")
    return "\n".join(lines) + "\n"


def blk_textonly(fid: int, group: bool = False) -> str:
    """Build [Face-N][org.kde.ksysguard.textonly][General] block.

    Args:
        fid: Numeric face ID.
        group: If True, group by total (display sum).
    """
    return (
        f"[Face-{fid}][org.kde.ksysguard.textonly][General]\n"
        f"groupByTotal={'true' if group else 'false'}\n"
    )


def blk_facegrid(
    fid: int,
    ncols: int | None = None,
    **kw: object,
) -> str:
    """Build [Face-N][org.kde.ksysguard.facegrid] block with mini-chart grid.

    Defaults: historyAmount=120, lineChartFillOpacity=100,
    showGridLines=false, showYAxisLabels=false.

    Args:
        fid: Numeric face ID.
        ncols: Number of grid columns (auto-calculated if None).
        **kw: Override parameters (e.g. rangeAutoY="false").
    """
    chart = "org.kde.ksysguard.linechart"
    defaults: dict[str, object] = {
        "historyAmount": 120,
        "lineChartFillOpacity": 100,
        "showGridLines": "false",
        "showYAxisLabels": "false",
    }
    defaults.update(kw)
    lines = [
        f"[Face-{fid}][org.kde.ksysguard.facegrid][General]",
    ]
    if ncols:
        lines.append(f"columnCount={ncols}")
    lines += [
        f"faceId={chart}",
        f"[Face-{fid}][FaceGrid][Appearance]",
        f"chartFace={chart}",
        "showTitle=false",
        f"[Face-{fid}][FaceGrid][{chart}][General]",
    ]
    for k, v in defaults.items():
        lines.append(f"{k}={v}")
    return "\n".join(lines) + "\n"


def blk_piechart(fid: int) -> str:
    """Build [Face-N][org.kde.ksysguard.piechart][General] block.

    Args:
        fid: Numeric face ID.
    """
    return f"[Face-{fid}][org.kde.ksysguard.piechart][General]\nshowLegend=true\n"


# --- Page layout ---


def blk_page(title_key: str, icon: str, lang: str = "fr") -> str:
    """Build [page] block with bilingual title.

    Args:
        title_key: i18n key for the page title (e.g. "page.cpu").
        icon: KDE icon name (e.g. "cpu", "memory").
        lang: Language code for the [en] suffix.
    """
    title_fr = t(title_key, lang=lang)
    title_en = t(title_key, lang="en")
    return (
        f"[page]\n"
        f"Title={title_fr}\ntitle={title_fr}\n"
        f"Title[en]={title_en}\ntitle[en]={title_en}\n"
        f"actionsFace=\nicon={icon}\nloadType=ondemand\n"
        f"margin=2\nversion=1\n"
    )


def blk_title_row(title_key: str, lang: str = "fr") -> str:
    """Build [page][row-0] page title row.

    Args:
        title_key: i18n key for the title.
        lang: Language code for the [en] suffix.
    """
    title_fr = t(title_key, lang=lang)
    title_en = t(title_key, lang="en")
    return (
        f"[page][row-0]\n"
        f"Title={title_fr}\ntitle={title_fr}\n"
        f"Title[en]={title_en}\ntitle[en]={title_en}\n"
        f"heightMode=minimum\nisTitle=true\nname=row-0\n"
    )


def blk_row(row: int, faces: list[int]) -> str:
    """Build [page][row-N] with columns containing faces.

    Args:
        row: Row number (1-indexed).
        faces: List of face IDs to place in columns.
    """
    lines = [
        f"[page][row-{row}]",
        "Title=",
        "heightMode=balanced",
        "isTitle=false",
        f"name=row-{row}",
    ]
    for ci, fid in enumerate(faces):
        lines += [
            f"[page][row-{row}][column-{ci}]",
            f"name=column-{ci}",
            "noMargins=false",
            "showBackground=true",
            f"[page][row-{row}][column-{ci}][section-0]",
            f"face=Face-{fid}",
            "isSeparator=false",
            "name=section-0",
        ]
    return "\n".join(lines) + "\n"
