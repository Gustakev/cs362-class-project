"""
Author: Kevin Gustafson
Date: 2026-02-23
Description: Gets info from Manifest.plist for the BackupModel.
"""

from pathlib import Path
import plistlib


def get_encryption_status(backup_root: Path) -> bool:
    """Gets the encryption status of the backup from Manifest.plist."""
    manifest_path = backup_root / "Manifest.plist"
    with manifest_path.open("rb") as f:
        manifest = plistlib.load(f)
    return manifest["IsEncrypted"]
