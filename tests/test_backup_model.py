"""
Author: Brendon Wong
Date: 2026-02-24
Description: Tests the process to build the BackupModel.
"""

import unittest 
from pydantic import ValidationError
from functional_components.backup_locator_and_validator.domain.backup_model import (
    Asset,
    Flags,
    Relationships,
    BackupMetadata,
    BackupModel,
    SourceDevice,
)


class TestValidData(unittest.TestCase):
    def test_asset_parses_valid_data(self):
        asset = Asset(
            asset_uuid="123",
            local_identifier="ABC",
            original_filename="IMG_0001.JPG",
            file_extension="JPG",
            uti_type="public.jpeg",
            creation_date="2024-01-01T12:00:00",
            modification_date="2024-01-01T12:00:00",
            timezone_offset="+00:00",
            backup_relative_path="Media/DCIM/100APPLE",
            backup_hashed_filename="hash.jpg",
            media_type="photo",
            subtype="standard",
            flags=Flags(),
            relationships=Relationships(),
        )

        self.assertEqual(asset.media_type, "photo")


class TestInvalidMedia(unittest.TestCase):
    def test_invalid_media_type_fails(self):
        """Audio is an invalid media type"""
        with self.assertRaises(ValidationError):
            Asset(
                asset_uuid="123",
                local_identifier="ABC",
                original_filename="IMG.JPG",
                file_extension="JPG",
                uti_type="public.jpeg",
                creation_date="2024-01-01",
                modification_date="2024-01-01",
                timezone_offset="+00:00",
                backup_relative_path="Media",
                backup_hashed_filename="hash.jpg",
                media_type="audio",  # invalid
                subtype="standard",
                flags=Flags(),
                relationships=Relationships(),
            )


class TestMissingField(unittest.TestCase):
    def test_missing_required_field_fails(self):
        """Missing local_identifier"""
        with self.assertRaises(ValidationError):
            Asset(
                asset_uuid="123",
                original_filename="IMG.JPG",
                file_extension="JPG",
                uti_type="public.jpeg",
                creation_date="2024-01-01",
                modification_date="2024-01-01",
                timezone_offset="+00:00",
                backup_relative_path="Media",
                backup_hashed_filename="hash.jpg",
                media_type="photo",
                subtype="standard",
                flags=Flags(),
                relationships=Relationships(),
            )


class TestBackupModel(unittest.TestCase):
    def test_backup_model_parses(self):
        backup = BackupModel(
            backup_metadata=BackupMetadata(
                backup_uuid="backup-1",
                backup_date="2024-01-01",
                is_encrypted=False,
                source_device=SourceDevice(
                    name="iPhone",
                    model="iPhone 13",
                    ios_version="17.1",
                ),
            ),
            assets=[],
            albums=[],
        )

        self.assertEqual(backup.backup_metadata.source_device.model, "iPhone 13")


if __name__ == "__main__":
    unittest.main()