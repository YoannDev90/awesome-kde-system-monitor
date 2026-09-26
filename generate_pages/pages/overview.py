"""Overview page generator.

Generates a dashboard overview with pie charts for CPU, GPU, Memory,
Swap, horizontal bars for Disks, and a network summary.

Faces:
  1001 - CPU pie chart
  1002 - GPU pie chart
  1003 - Memory pie chart
  1004 - Swap pie chart
  1005 - Disks horizontal bars
  1006 - Network summary (textonly)
  1007 - Applications table
"""

from ..blocks import (
    blk_appearance,
    blk_colors,
    blk_page,
    blk_piechart,
    blk_row,
    blk_sensors,
    blk_textonly,
    blk_title_row,
)
from ..constants import COLOR_CPU_TOTAL, COLOR_PRIMARY
from ..sensors import SensorGroups


def generate(groups: SensorGroups, lang: str = "fr") -> str | None:
    """Generate Page.page (overview dashboard).

    Args:
        groups: Dict returned by group_sensors().
        lang: Language code ("fr" or "en").

    Returns:
        .page file content, or None if no sensors available.
    """
    has_any = any([
        groups["cpu_all"],
        groups["gpu"],
        groups["memory"],
        groups["swap"],
        groups["disk_per"],
        groups["net_per"],
    ])
    if not has_any:
        return None

    P: list[str] = []
    P.append(blk_page("page.overview", "speedometer", lang))
    P.append(blk_title_row("page.overview", lang))

    faces: list[int] = []
    fid = 1001

    # --- CPU pie chart ---
    if "cpu/all/usage" in groups["cpu_all"]:
        P.append(blk_appearance(fid, "org.kde.ksysguard.piechart",
                                "page.cpu", lang))
        P.append(blk_sensors(fid, ["cpu/all/usage"], ["cpu/all/usage"]))
        P.append(blk_colors(fid, {"cpu/all/usage": COLOR_CPU_TOTAL}))
        P.append(blk_piechart(fid))
        faces.append(fid)
        fid += 1

    # --- GPU pie chart ---
    gpu_ids = [f"gpu/{g}/usage" for g in sorted(groups["gpu"])
               if "usage" in groups["gpu"][g]]
    if gpu_ids:
        P.append(blk_appearance(fid, "org.kde.ksysguard.piechart",
                                "page.gpu", lang))
        P.append(blk_sensors(fid, gpu_ids[:1], gpu_ids[:1]))
        P.append(blk_colors(fid, {s: COLOR_PRIMARY for s in gpu_ids[:1]}))
        P.append(blk_piechart(fid))
        faces.append(fid)
        fid += 1

    # --- Memory pie chart ---
    if "memory/physical/used" in groups["memory"]:
        P.append(blk_appearance(fid, "org.kde.ksysguard.piechart",
                                "page.memory", lang))
        P.append(blk_sensors(fid, ["memory/physical/used"],
                              ["memory/physical/used", "memory/physical/total"]))
        P.append(blk_colors(fid, {"memory/physical/used": COLOR_PRIMARY}))
        P.append(blk_piechart(fid))
        faces.append(fid)
        fid += 1

    # --- Swap pie chart ---
    if "memory/swap/used" in groups["swap"]:
        P.append(blk_appearance(fid, "org.kde.ksysguard.piechart",
                                "face.memory.swap_pct", lang))
        P.append(blk_sensors(fid, ["memory/swap/used"],
                              ["memory/swap/used", "memory/swap/total"]))
        P.append(blk_colors(fid, {"memory/swap/used": COLOR_PRIMARY}))
        P.append(blk_piechart(fid))
        faces.append(fid)
        fid += 1

    # --- Disks horizontal bars ---
    disk_ids = [f"disk/{d}/used" for d in sorted(groups["disk_per"])]
    if disk_ids:
        P.append(blk_appearance(fid, "org.kde.ksysguard.horizontalbars",
                                "page.disks", lang))
        P.append(blk_sensors(fid, disk_ids))
        P.append(blk_colors(fid, {s: COLOR_PRIMARY for s in disk_ids}))
        faces.append(fid)
        fid += 1

    # --- Network summary ---
    net_ids: list[str] = []
    for iface in sorted(groups["net_per"]):
        for metric in ["download", "upload"]:
            sid = f"network/{iface}/{metric}"
            if any(sid in s for s in groups["net_per"][iface]):
                net_ids.append(sid)
    if net_ids:
        P.append(blk_appearance(fid, "org.kde.ksysguard.textonly",
                                "page.network", lang))
        P.append(blk_sensors(fid, net_ids[:4]))
        dl_cols = COLOR_PRIMARY
        ul_cols = (39, 174, 96)
        P.append(blk_colors(fid, {
            s: dl_cols if "download" in s else ul_cols for s in net_ids[:4]
        }))
        P.append(blk_textonly(fid))
        faces.append(fid)
        fid += 1

    # --- Applications table ---
    P.append(blk_appearance(fid, "org.kde.ksysguard.applicationstable",
                            "face.os.info", lang, show_title=True))
    P.append(blk_textonly(fid))
    faces.append(fid)

    if not faces:
        return None

    # --- Layout ---
    row_size = 2
    for i in range(0, len(faces), row_size):
        row_num = i // row_size + 1
        row_faces = faces[i : i + row_size]
        P.append(blk_row(row_num, row_faces))

    return "\n".join(P) + "\n"
