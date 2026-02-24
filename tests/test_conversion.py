"""
Author: Sam Daughtry (Edited by Kevin Gustafson)
Date: 2026-02-23
Description: Tests the conversion feature.
"""

import unittest
from unittest.mock import patch, MagicMock

from functional_components.conversion_engine.app.convert_file import convert_asset
from functional_components.conversion_engine.domain.asset_to_convert import (
    AssetToConvert,
)
from functional_components.conversion_engine.domain.converted_asset import (
    ConvertedAsset,
)
from functional_components.backup_locator_and_validator.domain.backup_model import (
    Asset,
    Flags,
    Relationships,
)


def _make_asset(file_extension: str, backup_relative_path: str) -> Asset:
    """Build a minimal valid Asset for use in conversion tests."""
    return Asset(
        asset_uuid="test-uuid",
        local_identifier="test-local-id",
        original_filename=f"test.{file_extension.lower()}",
        file_extension=file_extension,
        uti_type=f"public.{file_extension.lower()}",
        creation_date="2026-01-01T00:00:00",
        modification_date="2026-01-01T00:00:00",
        timezone_offset="+00:00",
        backup_relative_path=backup_relative_path,
        backup_hashed_filename="abc123",
        media_type="photo" if file_extension.upper() in ("HEIC", "HEIF") else "video",
        subtype="standard",
        flags=Flags(),
        relationships=Relationships(),
    )


class TestConvertAsset(unittest.TestCase):

    @patch(
        "functional_components.conversion_engine.app.convert_file.store_temp_file"
    )
    @patch(
        "functional_components.conversion_engine.data.media_converter.Image"
    )
    def test_convert_heic_success(self, mock_image_module, mock_store_temp_file):
        mock_img = MagicMock()
        mock_image_module.open.return_value = mock_img
        mock_store_temp_file.return_value = "/tmp/iconvert_xyz/test.png"

        asset = _make_asset("HEIC", "/backup/abc123")
        asset_to_convert = AssetToConvert(
            asset_to_convert=asset,
            convert_type_dict={"HEIC": "PNG"},
        )

        result = convert_asset(asset_to_convert)

        mock_image_module.open.assert_called_once_with("/backup/abc123")
        mock_img.save.assert_called_once_with("/backup/abc123.png")
        mock_store_temp_file.assert_called_once_with("/backup/abc123.png")

        self.assertTrue(result.success)
        self.assertIsNotNone(result.converted_asset)
        self.assertEqual(
            result.converted_asset.backup_relative_path,
            "/tmp/iconvert_xyz/test.png",
        )
        self.assertEqual(
            result.converted_asset.original_filename, asset.original_filename
        )
        self.assertEqual(
            result.converted_asset.backup_hashed_filename,
            asset.backup_hashed_filename,
        )

    @patch(
        "functional_components.conversion_engine.app.convert_file.store_temp_file"
    )
    @patch(
        "functional_components.conversion_engine.data.media_converter.VideoFileClip"
    )
    def test_convert_mov_success(self, mock_video_clip, mock_store_temp_file):
        mock_video = MagicMock()
        mock_video_clip.return_value = mock_video
        mock_store_temp_file.return_value = "/tmp/iconvert_xyz/test.mp4"

        asset = _make_asset("MOV", "/backup/abc123")
        asset_to_convert = AssetToConvert(
            asset_to_convert=asset,
            convert_type_dict={"MOV": "MP4"},
        )

        result = convert_asset(asset_to_convert)

        mock_video_clip.assert_called_once_with("/backup/abc123")
        mock_video.write_videofile.assert_called_once_with(
            "/backup/abc123.mp4", codec="libx264"
        )
        mock_store_temp_file.assert_called_once_with("/backup/abc123.mp4")

        self.assertTrue(result.success)
        self.assertIsNotNone(result.converted_asset)
        self.assertEqual(
            result.converted_asset.backup_relative_path,
            "/tmp/iconvert_xyz/test.mp4",
        )
        self.assertEqual(
            result.converted_asset.original_filename, asset.original_filename
        )
        self.assertEqual(
            result.converted_asset.backup_hashed_filename,
            asset.backup_hashed_filename,
        )

    def test_no_conversion_rule_returns_failure(self):
        asset = _make_asset("HEIC", "/backup/abc123")
        asset_to_convert = AssetToConvert(
            asset_to_convert=asset,
            convert_type_dict={"MOV": "MP4"},  # No rule for HEIC
        )

        result = convert_asset(asset_to_convert)

        self.assertFalse(result.success)
        self.assertIsNone(result.converted_asset)
        self.assertIn("HEIC", result.error)

    def test_unsupported_extension_in_dict_returns_failure(self):
        asset = _make_asset("PNG", "/backup/abc123")
        asset_to_convert = AssetToConvert(
            asset_to_convert=asset,
            convert_type_dict={"PNG": "JPG"},  # In dict but not a supported conversion
        )

        result = convert_asset(asset_to_convert)

        self.assertFalse(result.success)
        self.assertIsNone(result.converted_asset)
        self.assertIn("PNG", result.error)

    @patch(
        "functional_components.conversion_engine.data.media_converter.Image"
    )
    def test_convert_heic_image_open_exception_returns_failure(
        self, mock_image_module
    ):
        mock_image_module.open.side_effect = OSError("File not found")

        asset = _make_asset("HEIC", "/backup/abc123")
        asset_to_convert = AssetToConvert(
            asset_to_convert=asset,
            convert_type_dict={"HEIC": "PNG"},
        )

        result = convert_asset(asset_to_convert)

        self.assertFalse(result.success)
        self.assertIsNone(result.converted_asset)
        self.assertIn("File not found", result.error)


if __name__ == "__main__":
    unittest.main()
    