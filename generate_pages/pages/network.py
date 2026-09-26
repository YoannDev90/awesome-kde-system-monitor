"""Network page generator.

Faces:
  2401 - Speed (linechart with regex pattern)
  2402 - Connection info (textonly)
  2403 - Cumulative totals (linechart)
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
from ..kconfig import kk, kp
from ..sensors import SensorGroups


def generate(groups: SensorGroups, lang: str = "fr") -> str | None:
    """Generate Reseau.page.

    Args:
        groups: Dict returned by group_sensors().
        lang: Language code ("fr" or "en").

    Returns:
        .page file content, or None if no network sensors available.
    """
    np = groups["net_per"]
    if not np:
        return None

    P: list[str] = []
    P.append(blk_page("page.network", "network-wired", lang))
    P.append(blk_title_row("page.network", lang))

    # --- Speed (linechart with pattern) ---
    P.append(blk_appearance(2401, "org.kde.ksysguard.linechart", "face.net.rate", lang))
    P.append(
        blk_sensors(
            2401,
            [
                kp(r"network/(?!all).*/download"),
                kp(r"network/(?!all).*/upload"),
            ],
        )
    )

    # Pattern colors + per-interface
    dl_k = kk(r"network/(?!all).*/download")
    ul_k = kk(r"network/(?!all).*/upload")
    clines = [
        "[Face-2401][SensorColors]",
        f"{dl_k}=41,128,185",
        f"{ul_k}=39,174,96",
    ]
    llines = ["[Face-2401][SensorLabels]"]
    for iface in sorted(np.keys()):
        clines.append(f"network/{iface}/download=41,128,185")
        clines.append(f"network/{iface}/upload=39,174,96")
        llines.append(f"network/{iface}/download={t('sensor.net.download', lang=lang)}")
        llines.append(f"network/{iface}/upload={t('sensor.net.upload', lang=lang)}")
    P.append("\n".join(clines) + "\n")
    P.append("\n".join(llines) + "\n")
    P.append(blk_linechart(2401, lineChartFillOpacity=15, showGridLines="true"))

    # --- Connection info (textonly) ---
    info_ids: list[str] = []
    icols: dict[str, tuple[int, int, int]] = {}
    ilabs: dict[str, str] = {}
    for iface in sorted(np.keys()):
        for sid in sorted(np[iface]):
            if "/download" not in sid and "/upload" not in sid:
                info_ids.append(sid)
                for pat, lbl_key, col in [
                    ("linkStrength", "sensor.temp.wifi_signal", (39, 174, 96)),
                    ("ipv4", "IPv4", (41, 128, 185)),
                    ("ipv6", "IPv6", (61, 233, 140)),
                    ("ssid", "SSID", (41, 128, 185)),
                    ("interface", "Interface", (41, 128, 185)),
                    ("type", "Type", (142, 68, 173)),
                ]:
                    if pat in sid:
                        ilabs[sid] = (
                            t(lbl_key, lang=lang) if lbl_key.startswith("sensor.") else lbl_key
                        )
                        icols[sid] = col
                        break
                else:
                    icols[sid] = (41, 128, 185)

    if info_ids:
        P.append(blk_appearance(2402, "org.kde.ksysguard.textonly", "face.net.connection", lang))
        P.append(blk_sensors(2402, info_ids[:6]))
        P.append(blk_colors(2402, icols))
        P.append(blk_labels(2402, ilabs))
        P.append(blk_textonly(2402))

    # --- Cumulative totals (linechart) ---
    cumul_ids: list[str] = []
    ccol: dict[str, tuple[int, int, int]] = {}
    clbl: dict[str, str] = {}
    for iface in sorted(np.keys()):
        for m in ["download", "upload"]:
            sid = f"network/{iface}/{m}Total"
            if any(sid in s for s in np.values()):
                cumul_ids.append(sid)
                ccol[sid] = (41, 128, 185) if "download" in m else (39, 174, 96)
                clbl[sid] = t(
                    "sensor.net.total_dl" if "download" in m else "sensor.net.total_ul", lang=lang
                )

    if cumul_ids:
        P.append(blk_appearance(2403, "org.kde.ksysguard.linechart", "face.net.cumul", lang))
        P.append(blk_sensors(2403, cumul_ids))
        P.append(blk_colors(2403, ccol))
        P.append(blk_labels(2403, clbl))
        P.append(blk_linechart(2403, lineChartFillOpacity=10))

    # --- Layout ---
    P.append(blk_row(1, [2401, 2402] if info_ids else [2401]))
    if cumul_ids:
        P.append(blk_row(2, [2403]))

    return "\n".join(P) + "\n"
