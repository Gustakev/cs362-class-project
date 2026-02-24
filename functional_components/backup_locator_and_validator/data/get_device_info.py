"""
Author: Kevin Gustafson
Date: 2026-02-15
Description: Gets info from Info.plist for the device portions of the
 BackupModel.
"""

from pathlib import Path
import plistlib


def get_device_info(backup_root: Path) -> dict:
    """Getting the object for device info."""
    info_path = backup_root / "Info.plist"
    with info_path.open("rb") as f:
        info = plistlib.load(f)
    return info
