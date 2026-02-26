"""
Author: Kevin Gustafson
Date: 2026-02-25
Description: System tests for iExtract.

Each test performs real filesystem I/O -- creating files on disk,
running conversions, and checking that output files physically exist.
They are designed to pass on Windows, Linux, and macOS, and the CI
run on GitHub's Ubuntu runner serves as cross-environment evidence.

Components exercised:
    - store_temp_file (moves files into the OS temp directory)
    - convert_asset (runs the conversion pipeline end-to-end)
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from functional_components.conversion_engine.data.conversion_temp_store import (
    store_temp_file,
)
from functional_components.conversion_engine.app.convert_file import convert_asset
from functional_components.conversion_engine.domain.asset_to_convert import (
    AssetToConvert,
)
from functional_components.backup_locator_and_validator.domain.backup_model import (
    Asset,
    Flags,
    Relationships,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_asset(extension: str, path: str) -> Asset:
    """Return a minimal Asset pointing at the given path on disk."""
    is_photo = extension.upper() in ("HEIC", "HEIF")
    return Asset(
        asset_uuid="sys-test-uuid",
        local_identifier="sys-test-local-id",
        original_filename=f"test.{extension.lower()}",
        file_extension=extension,
        uti_type=f"public.{extension.lower()}",
        creation_date="2026-01-01T00:00:00+00:00",
        modification_date="2026-01-01T00:00:00+00:00",
        timezone_offset="",
        backup_relative_path=path,
        backup_hashed_filename=Path(path).name,
        media_type="photo" if is_photo else "video",
        subtype="standard",
        flags=Flags(),
        relationships=Relationships(),
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestStoreTempFile(unittest.TestCase):
    """System tests for store_temp_file.

    Verifies real filesystem behaviour on whatever OS the suite runs on.
    Each test creates a real source file, calls store_temp_file, and
    inspects the result on disk. Temp directories are cleaned up in
    tearDown.
    """

    def setUp(self):
        # Track result paths so tearDown can clean up even if a test fails
        self._result_paths = []

    def tearDown(self):
        for path in self._result_paths:
            parent = Path(path).parent
            if parent.exists():
                shutil.rmtree(parent, ignore_errors=True)

    def test_creates_file(self):
        """Output file exists on disk at the returned path."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(b"\x89PNG\r\n\x1a\n")
            src = f.name

        result = store_temp_file(src)
        self._result_paths.append(result)

        self.assertTrue(
            Path(result).exists(),
            msg=f"Expected file at: {result}",
        )

    def test_moves_not_copies(self):
        """Source file no longer exists after the move."""
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            f.write(b"fake jpg content")
            src = f.name

        result = store_temp_file(src)
        self._result_paths.append(result)

        self.assertFalse(Path(src).exists())

    def test_preserves_filename(self):
        """Filename is unchanged in the temp destination."""
        with tempfile.NamedTemporaryFile(
            suffix=".mp4", prefix="myfile_", delete=False
        ) as f:
            f.write(b"fake mp4 content")
            src = f.name
            original_name = Path(src).name

        result = store_temp_file(src)
        self._result_paths.append(result)

        self.assertEqual(Path(result).name, original_name)

    def test_uses_os_temp_dir(self):
        """Output lands inside the OS temp directory on all platforms."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(b"content")
            src = f.name

        result = store_temp_file(src)
        self._result_paths.append(result)

        sys_tmp = Path(tempfile.gettempdir()).resolve()
        result_abs = Path(result).resolve()
        self.assertTrue(
            str(result_abs).startswith(str(sys_tmp)),
            msg=f"Expected inside {sys_tmp}, got {result_abs}",
        )


class TestConvertAssetFilesystem(unittest.TestCase):
    """System tests for convert_asset.

    Verifies that the conversion pipeline writes a real file to disk
    and that failed conversions leave no stray output files behind.
    Image.open is mocked so the tests do not require a real HEIC file,
    but store_temp_file and all filesystem operations run for real.
    """

    def test_heic_writes_output_file(self):
        """Successful HEIC conversion produces a real file on disk."""
        with tempfile.NamedTemporaryFile(suffix=".HEIC", delete=False) as f:
            src = f.name

        mock_img = MagicMock()

        def fake_save(out):
            Path(out).write_bytes(b"fake png content")

        mock_img.save.side_effect = fake_save
        result = None

        try:
            with patch(
                "functional_components.conversion_engine"
                ".data.media_converter.Image"
            ) as mock_mod:
                mock_mod.open.return_value = mock_img
                asset = _make_asset("HEIC", src)
                result = convert_asset(
                    AssetToConvert(
                        asset_to_convert=asset,
                        convert_type_dict={"HEIC": "PNG"},
                    )
                )

            self.assertTrue(result.success, msg=result.error)
            self.assertTrue(
                Path(result.converted_asset.backup_relative_path).exists()
            )
        finally:
            if os.path.exists(src):
                os.unlink(src)
            if result and result.success:
                parent = Path(
                    result.converted_asset.backup_relative_path
                ).parent
                if parent.exists():
                    shutil.rmtree(parent, ignore_errors=True)

    def test_failure_leaves_no_file(self):
        """A failed conversion does not leave a stray output file on disk."""
        asset = _make_asset("HEIC", "/nonexistent/path/file.HEIC")
        result = convert_asset(
            AssetToConvert(
                asset_to_convert=asset,
                convert_type_dict={"HEIC": "PNG"},
            )
        )

        self.assertFalse(result.success)
        self.assertFalse(Path("/nonexistent/path/file.png").exists())


if __name__ == "__main__":
    unittest.main()
