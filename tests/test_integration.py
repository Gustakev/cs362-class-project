"""
Author: Kevin Gustafson
Date: 2026-02-25
Description: Integration tests for iExtract.

Each test exercises multiple real components working together with no
mocking. A minimal synthetic backup is written to a temp directory
before each test and cleaned up after.

Components exercised together:
    - get_device_info (reads Info.plist)
    - get_encryption_status (reads Manifest.plist)
    - get_photos_sqlite_path (queries Manifest.db)
    - find_album_asset_join_table / find_join_table_columns (schema discovery)
    - get_albums / build_albums
    - get_assets / build_assets
    - build_backup_model (orchestrates all of the above)
"""

import plistlib
import sqlite3
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from functional_components.backup_locator_and_validator.app.backup_model_builder import (
    build_backup_model,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_minimal_backup(root: Path) -> None:
    """Write the minimum files needed for build_backup_model to succeed.

    Creates:
        Info.plist      -- device metadata
        Manifest.plist  -- encryption flag
        Manifest.db     -- file registry with a Photos.sqlite entry
        ab/<hash>       -- empty but schema-valid Photos.sqlite
    """
    # Info.plist
    info = {
        "Device Name": "Integration Test iPhone",
        "Product Type": "iPhone15,2",
        "Product Version": "17.0",
        "GUID": "AABBCCDD11223344AABBCCDD11223344",
        "Last Backup Date": datetime(2026, 1, 1, 12, 0, 0),
    }
    with (root / "Info.plist").open("wb") as f:
        plistlib.dump(info, f)

    # Manifest.plist
    with (root / "Manifest.plist").open("wb") as f:
        plistlib.dump({"IsEncrypted": False}, f)

    # Photos.sqlite -- empty tables matching the real iOS schema
    fake_id = "ab" + "c" * 38  # 40-char hex-like file ID
    photos_dir = root / fake_id[:2]
    photos_dir.mkdir(parents=True, exist_ok=True)
    photos_path = photos_dir / fake_id

    conn = sqlite3.connect(photos_path)
    conn.execute(
        "CREATE TABLE ZASSET ("
        "Z_PK INTEGER PRIMARY KEY, ZUUID TEXT, ZFILENAME TEXT,"
        "ZDIRECTORY TEXT, ZDATECREATED REAL, ZMODIFICATIONDATE REAL,"
        "ZKIND INTEGER, ZKINDSUBTYPE INTEGER, ZFAVORITE INTEGER,"
        "ZHIDDEN INTEGER, ZTRASHEDSTATE INTEGER, ZAVALANCHEUUID TEXT,"
        "ZAVALANCHEPICKTYPE INTEGER, ZMEDIAGROUPUUID TEXT,"
        "ZUNIFORMTYPEIDENTIFIER TEXT)"
    )
    conn.execute(
        "CREATE TABLE ZADDITIONALASSETATTRIBUTES ("
        "Z_PK INTEGER PRIMARY KEY, ZASSET INTEGER, ZORIGINALFILENAME TEXT)"
    )
    conn.execute(
        "CREATE TABLE ZGENERICALBUM ("
        "Z_PK INTEGER PRIMARY KEY, ZUUID TEXT, ZTITLE TEXT,"
        "ZKIND INTEGER, ZCUSTOMSORTKEY REAL, ZCUSTOMSORTASCENDING INTEGER,"
        "ZCACHEDCOUNT INTEGER)"
    )
    conn.execute(
        "CREATE TABLE Z_3ASSETS ("
        "Z_3ALBUMS INTEGER, Z_3ASSETS INTEGER, Z_FOK_3ASSETS INTEGER)"
    )
    conn.commit()
    conn.close()

    # Manifest.db -- maps the fake file ID to Photos.sqlite's logical path
    mconn = sqlite3.connect(root / "Manifest.db")
    mconn.execute(
        "CREATE TABLE Files (fileID TEXT PRIMARY KEY, relativePath TEXT)"
    )
    mconn.execute(
        "INSERT INTO Files VALUES (?, ?)",
        (fake_id, "Media/PhotoData/Photos.sqlite"),
    )
    mconn.commit()
    mconn.close()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestBuildBackupModelIntegration(unittest.TestCase):
    """Integration tests for build_backup_model using real files on disk.

    setUp writes a minimal synthetic backup to a temp directory.
    tearDown removes it. No mocking is used in any test.
    """

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.backup_root = Path(self.temp_dir.name)
        _build_minimal_backup(self.backup_root)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_success(self):
        """Returns a successful result when all backup files are present."""
        result = build_backup_model(self.backup_root)

        self.assertTrue(result.success, msg=result.error)
        self.assertIsNotNone(result.backup_model)

    def test_device_metadata(self):
        """Device name, model, and iOS version are read from Info.plist."""
        result = build_backup_model(self.backup_root)

        device = result.backup_model.backup_metadata.source_device
        self.assertEqual(device.name, "Integration Test iPhone")
        self.assertEqual(device.model, "iPhone15,2")
        self.assertEqual(device.ios_version, "17.0")

    def test_backup_uuid(self):
        """GUID from Info.plist is stored as backup_uuid in the model."""
        result = build_backup_model(self.backup_root)

        self.assertEqual(
            result.backup_model.backup_metadata.backup_uuid,
            "AABBCCDD11223344AABBCCDD11223344",
        )

    def test_encryption_status(self):
        """is_encrypted reflects the IsEncrypted value in Manifest.plist."""
        result = build_backup_model(self.backup_root)

        self.assertFalse(result.backup_model.backup_metadata.is_encrypted)

    def test_empty_db_yields_empty_model(self):
        """Empty but valid Photos.sqlite produces zero assets and albums."""
        result = build_backup_model(self.backup_root)

        self.assertEqual(result.backup_model.assets, [])
        self.assertEqual(result.backup_model.albums, [])

    def test_encrypted_returns_failure(self):
        """IsEncrypted=True in Manifest.plist causes a failure result."""
        with (self.backup_root / "Manifest.plist").open("wb") as f:
            plistlib.dump({"IsEncrypted": True}, f)

        result = build_backup_model(self.backup_root)

        self.assertFalse(result.success)
        self.assertIn("encrypted", result.error.lower())

    def test_missing_plist_returns_failure(self):
        """Absent Info.plist causes a failure result, not an exception."""
        (self.backup_root / "Info.plist").unlink()

        result = build_backup_model(self.backup_root)

        self.assertFalse(result.success)
        self.assertIsNone(result.backup_model)


if __name__ == "__main__":
    unittest.main()
