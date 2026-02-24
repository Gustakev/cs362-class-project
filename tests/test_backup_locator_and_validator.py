"""
Author: Brendon Wong (Edited by Kevin Gustafson)
Date: 2026-02-23
Description: Tests the process to build the BackupModel.
"""

import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from functional_components.backup_locator_and_validator.app.backup_model_builder import (
    build_device,
    build_backup_model,
)
from functional_components.backup_locator_and_validator.domain.backup_model import (
    SourceDevice,
)


MOCK_RAW_INFO = {
    "Device Name": "Test iPhone",
    "Product Type": "iPhone15,2",
    "Product Version": "17.3.1",
    "GUID": "D7A5EB27206B918EB006E38E4B84C87F",
    "Last Backup Date": datetime(2026, 1, 21, 11, 38, 37),
}


class TestBuildDevice(unittest.TestCase):

    def test_build_device_success(self):
        device = build_device(MOCK_RAW_INFO)

        self.assertEqual(device.name, "Test iPhone")
        self.assertEqual(device.model, "iPhone15,2")
        self.assertEqual(device.ios_version, "17.3.1")

    def test_build_device_missing_key_raises(self):
        incomplete_info = {"Device Name": "Test iPhone"}

        with self.assertRaises(KeyError):
            build_device(incomplete_info)


class TestBuildBackupModel(unittest.TestCase):

    def setUp(self):
        self.backup_root = Path("fake/root")

    @patch(
    "functional_components.backup_locator_and_validator.app"
    ".backup_model_builder.build_assets"
    )
    @patch(
        "functional_components.backup_locator_and_validator.app"
        ".backup_model_builder.build_membership_lookup"
    )
    @patch(
        "functional_components.backup_locator_and_validator.app"
        ".backup_model_builder.get_asset_album_memberships"
    )
    @patch(
        "functional_components.backup_locator_and_validator.app"
        ".backup_model_builder.get_assets"
    )
    @patch(
        "functional_components.backup_locator_and_validator.app"
        ".backup_model_builder.build_albums"
    )
    @patch(
        "functional_components.backup_locator_and_validator.app"
        ".backup_model_builder.get_albums"
    )
    @patch(
        "functional_components.backup_locator_and_validator.app"
        ".backup_model_builder.find_join_table_columns"
    )
    @patch(
        "functional_components.backup_locator_and_validator.app"
        ".backup_model_builder.find_album_asset_join_table"
    )
    @patch(
        "functional_components.backup_locator_and_validator.app"
        ".backup_model_builder.open_db"
    )
    @patch(
        "functional_components.backup_locator_and_validator.app"
        ".backup_model_builder.get_photos_sqlite_path"
    )
    @patch(
        "functional_components.backup_locator_and_validator.app"
        ".backup_model_builder.get_encryption_status"
    )
    @patch(
        "functional_components.backup_locator_and_validator.app"
        ".backup_model_builder.get_device_info"
    )
    def test_build_backup_model_success(
        self,
        mock_get_device_info,
        mock_get_encryption_status,
        mock_get_photos_sqlite_path,
        mock_open_db,
        mock_find_join_table,
        mock_find_join_cols,
        mock_get_albums,
        mock_build_albums,
        mock_get_assets,
        mock_get_asset_album_memberships,
        mock_build_membership_lookup,
        mock_build_assets,
    ):
        mock_get_device_info.return_value = MOCK_RAW_INFO
        mock_get_encryption_status.return_value = False
        mock_get_photos_sqlite_path.return_value = Path("fake/Photos.sqlite")
        mock_open_db.return_value.__enter__ = lambda s: s
        mock_open_db.return_value.__exit__ = lambda s, *a: False
        mock_find_join_table.return_value = "Z_33ASSETS"
        mock_find_join_cols.return_value = {
            "album_fk": "Z_33ALBUMS",
            "asset_fk": "Z_3ASSETS",
            "sort_col": "Z_FOK_3ASSETS",
        }
        mock_get_albums.return_value = []
        mock_build_albums.return_value = []
        mock_get_assets.return_value = []
        mock_get_asset_album_memberships.return_value = []
        mock_build_membership_lookup.return_value = {}
        mock_build_assets.return_value = []

        result = build_backup_model(self.backup_root)

        self.assertTrue(result.success)
        self.assertIsNotNone(result.backup_model)
        self.assertEqual(
            result.backup_model.backup_metadata.backup_uuid,
            "D7A5EB27206B918EB006E38E4B84C87F",
        )
        self.assertEqual(
            result.backup_model.backup_metadata.backup_date,
            "2026-01-21T11:38:37",
        )
        self.assertFalse(result.backup_model.backup_metadata.is_encrypted)
        self.assertEqual(
            result.backup_model.backup_metadata.source_device.name,
            "Test iPhone",
        )

    @patch(
        "functional_components.backup_locator_and_validator.app"
        ".backup_model_builder.get_encryption_status"
    )
    @patch(
        "functional_components.backup_locator_and_validator.app"
        ".backup_model_builder.get_device_info"
    )
    def test_build_backup_model_encrypted_returns_failure(
        self, mock_get_device_info, mock_get_encryption_status
    ):
        mock_get_device_info.return_value = MOCK_RAW_INFO
        mock_get_encryption_status.return_value = True

        result = build_backup_model(self.backup_root)

        self.assertFalse(result.success)
        self.assertIsNone(result.backup_model)
        self.assertIn("encrypted", result.error.lower())

    @patch(
        "functional_components.backup_locator_and_validator.app"
        ".backup_model_builder.get_encryption_status"
    )
    @patch(
        "functional_components.backup_locator_and_validator.app"
        ".backup_model_builder.get_device_info"
    )
    def test_build_backup_model_device_info_fails(
        self, mock_get_device_info, mock_get_encryption_status
    ):
        mock_get_device_info.side_effect = FileNotFoundError("Info.plist not found")
        mock_get_encryption_status.return_value = False

        result = build_backup_model(self.backup_root)

        self.assertFalse(result.success)
        self.assertIsNone(result.backup_model)
        self.assertIn("Info.plist not found", result.error)

    @patch(
        "functional_components.backup_locator_and_validator.app"
        ".backup_model_builder.get_encryption_status"
    )
    @patch(
        "functional_components.backup_locator_and_validator.app"
        ".backup_model_builder.get_device_info"
    )
    def test_build_backup_model_manifest_fails(
        self, mock_get_device_info, mock_get_encryption_status
    ):
        mock_get_device_info.return_value = MOCK_RAW_INFO
        mock_get_encryption_status.side_effect = FileNotFoundError(
            "Manifest.plist not found"
        )

        result = build_backup_model(self.backup_root)

        self.assertFalse(result.success)
        self.assertIsNone(result.backup_model)
        self.assertIn("Manifest.plist not found", result.error)


if __name__ == "__main__":
    unittest.main()