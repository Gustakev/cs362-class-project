"""
Author: Brendon Wong
Date: 2026-02-19
Description: Tests the process to build the BackupModel.
"""

import unittest
from pathlib import Path
from unittest.mock import patch

from functional_components.backup_locator_and_validator.app.backup_model_builder import build_device, build_backup_model
from functional_components.backup_locator_and_validator.domain.backup_model import SourceDevice

class TestBackupModelBuilder(unittest.TestCase):
    def setUp(self):
        self.backup_root = Path("fake/root")

    @patch("functional_components.backup_locator_and_validator.app.backup_model_builder.get_device_info")
    def test_build_device_success(self, mock_get_device_info):
        mock_get_device_info.return_value = {
            "Device Name": "Test iPhone",
            "Product Type": "iPhone15",
            "Product Version": "17.3.1",
        }

        device = build_device(self.backup_root)

        self.assertEqual(device.name, "Test iPhone")
        self.assertEqual(device.model, "iPhone15")
        self.assertEqual(device.ios_version, "17.3.1")


    @patch("functional_components.backup_locator_and_validator.app.backup_model_builder.build_device")
    def test_build_backup_model_success(self, mock_build_device):
        mock_build_device.return_value = SourceDevice(
            name="Test iPhone",
            model="iPhone15",
            ios_version="17.3.1"
        )

        result = build_backup_model(self.backup_root)

        self.assertTrue(result.success)
        self.assertIsNotNone(result.backup_model)
        self.assertEqual(result.backup_model.backup_metadata.backup_uuid, "test")
        self.assertEqual(result.backup_model.backup_metadata.source_device.name, "Test iPhone")


    @patch("functional_components.backup_locator_and_validator.app.backup_model_builder.build_device")
    def test_build_backup_model_fail(self, mock_build_device):
        mock_build_device.side_effect = RuntimeError("boom")

        result = build_backup_model(self.backup_root)

        self.assertFalse(result.success)
        self.assertIsNone(getattr(result, "backup_model", None))
        self.assertIn("Failed loading device info.", result.error)
        self.assertIn("boom", result.error)


if __name__ == "__main__":
    unittest.main()