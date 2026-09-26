"""generate_pages — Generate .page files for plasma-systemmonitor.

Discovers system sensors via D-Bus (ksystemstats), groups them by
functional type, and generates KConfig pages adapted to detected
hardware. Supports French (default) and English via i18n.
"""

__version__ = "1.0.0"
