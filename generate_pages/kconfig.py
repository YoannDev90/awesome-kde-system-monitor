"""KConfig formatting helpers for .page files.

Handles regex escaping differences between:
- highPrioritySensorIds: requires 4 backslashes (kp)
- SensorColors/SensorLabels keys: requires 2 backslashes (kk)
"""


def kp(raw_regex):
    """Escape a regex for highPrioritySensorIds (4 backslashes in file).

    KConfig double-escapes backslashes in value strings, so a literal
    backslash in the regex pattern must appear as \\\\ in the file.
    """
    return raw_regex.replace("\\", "\\\\\\\\")


def kk(raw_regex):
    """Escape a regex for SensorColors/SensorLabels keys (2 backslashes).

    KConfig keys use single-escape, so a literal backslash appears
    as \\ in the file.
    """
    return raw_regex.replace("\\", "\\\\")
