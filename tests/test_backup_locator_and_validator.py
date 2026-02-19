"""
Author: Brendon Wong
Date: 2026-02-19
Description: Tests the process to build the BackupModel.
"""

import unittest
from pathlib import Path
from unittest.mock import patch

from functional_components.backup_locator_and_validator.app.backup_model_builder import build_device


class TestBackupModelBuilder(unittest.TestCase):
    def setUp(self):
        self.backup_root = Path("fake/root")

    @patch("functional_components.backup_locator_and_validator.app.backup_model_builder.get_device_info")
    def test_build_device_success(self, mock_get_device_info):
        mock_get_device_info.return_value = {
            "Device Name": "Test iPhone",
            "Product Type": "iPhone15,3",
            "Product Version": "17.3.1",
        }

        device = build_device(self.backup_root)

        self.assertEqual(device.name, "Test iPhone")
        self.assertEqual(device.model, "iPhone15,3")
        self.assertEqual(device.ios_version, "17.3.1")



if __name__ == "__main__":
    unittest.main()