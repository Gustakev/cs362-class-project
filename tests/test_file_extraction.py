"""
Author: Sam Daughtry
Date: 2026-03-01
Description: Unit tests for the file extraction engine helpers and main loop.
"""

import os
import tempfile
import unittest
from pathlib import Path
from typing import Dict

from functional_components.backup_locator_and_validator.domain.backup_model import (
    Asset,
    Album,
    BackupMetadata,
    BackupModel,
    Flags,
    Relationships,
    SourceDevice,
)
from functional_components.file_extraction_engine.app.extract_files import (
    run_extraction_engine,
)
from functional_components.file_extraction_engine.app.extraction_helpers import (
    get_active_collections,
    get_dest_name,
    maybe_convert,
)
from functional_components.file_extraction_engine.domain.blacklist import (
    Blacklist,
    ListEntry,
)
from functional_components.file_extraction_engine.domain.collection_ref import (
    CollectionRef,
)


def _make_asset(
    asset_uuid: str,
    original_filename: str,
    file_extension: str,
    backup_relative_path: str,
    user_albums=None,
    smart_folders=None,
    is_primary=False,
) -> Asset:
    if user_albums is None:
        user_albums = []
    if smart_folders is None:
        smart_folders = []
    return Asset(
        asset_uuid=asset_uuid,
        local_identifier="id",
        original_filename=original_filename,
        file_extension=file_extension,
        uti_type="public.image",
        creation_date="2026-03-01T00:00:00",
        modification_date="2026-03-01T00:00:00",
        timezone_offset="+00:00",
        backup_relative_path=backup_relative_path,
        backup_hashed_filename="hash",
        media_type="photo",
        subtype="standard",
        flags=Flags(),
        relationships=Relationships(user_albums=user_albums, smart_folders=smart_folders),
        is_primary_burst_frame=is_primary,
    )


class TestExtractionHelpers(unittest.TestCase):
    def test_get_dest_name_conversion(self):
        asset = _make_asset("u", "photo.jpg", "JPG", "/src/photo.jpg")
        converted = asset.model_copy(update={"backup_relative_path": "/tmp/photo.png"})
        name = get_dest_name(asset, converted)
        self.assertEqual(name, "photo.png")

    def test_get_dest_name_no_conversion(self):
        asset = _make_asset("u", "photo.jpg", "JPG", "/src/photo.jpg")
        name = get_dest_name(asset, asset)
        self.assertEqual(name, "photo.jpg")

    def test_get_active_collections(self):
        # build a blacklist that excludes one user album and one NUA
        blacklist = Blacklist(current_list=[
            ListEntry(name="Album A", is_NUA=False),
            ListEntry(name="favorites", is_NUA=True),
        ])
        mapping = {"uuidA": "Album A", "uuidB": "Album B"}
        asset = _make_asset(
            "u1",
            "f.jpg",
            "JPG",
            "/src/f.jpg",
            user_albums=["uuidA", "uuidB"],
            smart_folders=["favorites", "selfies"],
        )
        cols = get_active_collections(asset, blacklist, mapping)
        titles = {c.title for c in cols}
        self.assertIn("Album B", titles)
        self.assertIn("nua_selfies", titles)
        self.assertNotIn("Album A", titles)
        self.assertNotIn("nua_favorites", titles)

    def test_maybe_convert_no_rule(self):
        asset = _make_asset("u", "f.jpg", "JPG", "/src/f.jpg")
        out = maybe_convert(asset, {})
        self.assertIs(out, asset)


class TestRunExtractionEngine(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.output = Path(self.temp.name) / "out"
        os.makedirs(self.output, exist_ok=True)

        # create two dummy files that will be copied by extraction
        self.src_dir = Path(self.temp.name) / "src"
        os.makedirs(self.src_dir, exist_ok=True)
        (self.src_dir / "a.jpg").write_text("a")
        (self.src_dir / "b.jpg").write_text("b")

        self.backup_meta = BackupMetadata(
            backup_uuid="x",
            backup_date="2026-03-01",
            is_encrypted=False,
            source_device=SourceDevice(name="d", model="m", ios_version="v"),
        )

    def tearDown(self):
        self.temp.cleanup()

    def test_basic_extraction_no_symlinks(self):
        # two assets in separate albums
        album1 = Album(album_uuid="uuid1", title="One", type="user", sort_order="none", asset_count=1)
        album2 = Album(album_uuid="uuid2", title="Two", type="user", sort_order="none", asset_count=1)
        asset1 = _make_asset("u1", "a.jpg", "JPG", str(self.src_dir / "a.jpg"), user_albums=["uuid1"])
        asset2 = _make_asset("u2", "b.jpg", "JPG", str(self.src_dir / "b.jpg"), user_albums=["uuid2"])
        model = BackupModel(
            backup_metadata=self.backup_meta,
            assets=[asset1, asset2],
            albums=[album1, album2],
        )
        progress = type("P", (), {"percent": 0})()
        blacklist = Blacklist(current_list=[])

        run_extraction_engine(
            model,
            blacklist,
            self.output,
            os_supports_symlinks=False,
            user_set_symlinks=False,
            convert_type_dict={},
            progress=progress,
        )

        # verify files copied into named album directories
        self.assertTrue((self.output / "One" / "a.jpg").exists())
        self.assertTrue((self.output / "Two" / "b.jpg").exists())
        self.assertEqual(progress.percent, 100)

    def test_unassigned_asset_goes_to_non_exclusive(self):
        # asset with no albums should land in non_exclusive_assets
        asset = _make_asset("u3", "a.jpg", "JPG", str(self.src_dir / "a.jpg"))
        model = BackupModel(
            backup_metadata=self.backup_meta,
            assets=[asset],
            albums=[],
        )
        progress = type("P", (), {"percent": 0})()
        blacklist = Blacklist(current_list=[])

        run_extraction_engine(
            model,
            blacklist,
            self.output,
            os_supports_symlinks=False,
            user_set_symlinks=False,
            convert_type_dict={},
            progress=progress,
        )

        self.assertTrue((self.output / "non_exclusive_assets" / "a.jpg").exists())
        self.assertEqual(progress.percent, 100)


if __name__ == "__main__":
    unittest.main()
