"""
Author: Sam Daughtry
Date: 2026-03-08
Description: Unit tests for the service functions.
"""

import unittest
from functional_components.services import BackupService
from functional_components.backup_locator_and_validator.domain.backup_model import (
    BackupModel,
    BackupMetadata,
    SourceDevice,
)


class TestBackupServiceMetadataFormatting(unittest.TestCase):
    def setUp(self):
        self.service = BackupService()

    def test_no_backup_loaded(self):
        # should gracefully return an error message
        self.assertEqual(self.service.get_formatted_device_metadata(), "No backup loaded.")

    def test_brand_lookup_added_to_output(self):
        # construct a minimal backup model with a known technical identifier
        device = SourceDevice(name="iPhone", model="iPhone12,1", ios_version="16.0")
        metadata = BackupMetadata(
            backup_uuid="uuid",
            backup_date="2024-01-01T10:00:00",
            is_encrypted=False,
            source_device=device,
        )
        self.service.current_model = BackupModel(
            backup_metadata=metadata,
            assets=[],
            albums=[],
        )

        output = self.service.get_formatted_device_metadata()
        # the mapping should map iPhone12,1 -> "iPhone 11"
        self.assertIn("iPhone 11", output)
        # ensure the formatted model string is also present
        self.assertIn("iPhone 12", output)


class TestSettingsServiceSmartAlbum(unittest.TestCase):
    """Unit tests for smart album exclusion functionality in SettingsService."""

    def setUp(self):
        from functional_components.services import SettingsService
        self.settings = SettingsService()

    def test_initial_state_no_exclusions(self):
        """Test that smart album exclusions start empty."""
        self.assertEqual(self.settings.excluded_smart_albums, set())

    def test_toggle_smart_album_exclusion_enables(self):
        """Test enabling smart album exclusion."""
        result = self.settings.toggle_smart_album_exclusion("hidden")
        self.assertIn("hidden", self.settings.excluded_smart_albums)
        self.assertIn("now excluded", result)

    def test_toggle_smart_album_exclusion_disables(self):
        """Test disabling smart album exclusion."""
        # First enable it
        self.settings.toggle_smart_album_exclusion("hidden")
        self.assertIn("hidden", self.settings.excluded_smart_albums)

        # Then disable it
        result = self.settings.toggle_smart_album_exclusion("hidden")
        self.assertNotIn("hidden", self.settings.excluded_smart_albums)
        self.assertIn("no longer excluded", result)

    def test_toggle_multiple_smart_albums(self):
        """Test toggling multiple smart albums independently."""
        # Enable hidden
        self.settings.toggle_smart_album_exclusion("hidden")
        self.assertIn("hidden", self.settings.excluded_smart_albums)
        self.assertNotIn("recently_deleted", self.settings.excluded_smart_albums)

        # Enable recently deleted
        self.settings.toggle_smart_album_exclusion("recently_deleted")
        self.assertIn("hidden", self.settings.excluded_smart_albums)
        self.assertIn("recently_deleted", self.settings.excluded_smart_albums)

        # Disable hidden
        self.settings.toggle_smart_album_exclusion("hidden")
        self.assertNotIn("hidden", self.settings.excluded_smart_albums)
        self.assertIn("recently_deleted", self.settings.excluded_smart_albums)

    def test_get_engine_blacklist_includes_excluded_smart_albums(self):
        """Test that excluded smart albums are added to the engine blacklist."""
        # Enable exclusions
        self.settings.toggle_smart_album_exclusion("hidden")
        self.settings.toggle_smart_album_exclusion("recently_deleted")

        # Get the base blacklist
        bl = self.settings.get_engine_blacklist()

        # Simulate what ExportService does - append excluded NUAs
        from functional_components.file_extraction_engine.domain.blacklist import ListEntry
        for nua in self.settings.excluded_smart_albums:
            bl.current_list.append(ListEntry(nua))

        # Verify both are in the blacklist
        names = [e.name for e in bl.current_list]
        self.assertIn("hidden", names)
        self.assertIn("recently_deleted", names)


class TestSmartAlbumIntegration(unittest.TestCase):
    """Integration tests verifying smart album exclusion affects asset extraction."""

    def _create_test_asset(self, user_albums=None, smart_folders=None):
        """Helper to create a test asset with specified relationships."""
        from functional_components.backup_locator_and_validator.domain.backup_model import Asset

        raw = {
            "asset_uuid": "test-uuid",
            "local_identifier": "test-id",
            "original_filename": "test.jpg",
            "file_extension": "JPG",
            "uti_type": "public.jpeg",
            "creation_date": "2020-01-01",
            "modification_date": "2020-01-01",
            "timezone_offset": "0",
            "backup_relative_path": "path",
            "backup_hashed_filename": "hash",
            "media_type": "photo",
            "subtype": "standard",
            "flags": {"is_favorite": False, "is_hidden": False, "is_recently_deleted": False, "is_selfie": False},
            "relationships": {
                "user_albums": user_albums or [],
                "burst_album": None,
                "smart_folders": smart_folders or []
            },
        }
        return Asset.parse_obj(raw)

    def test_asset_in_excluded_smart_album_only_completely_excluded(self):
        """Test that assets only in excluded smart albums are not extracted."""
        from functional_components.file_extraction_engine.app.extraction_helpers import get_active_collections
        from functional_components.file_extraction_engine.domain.blacklist import Blacklist, ListEntry

        # Asset in both hidden and recently_deleted smart albums
        asset = self._create_test_asset(smart_folders=["hidden", "recently_deleted"])

        # Blacklist with hidden excluded
        bl = Blacklist(current_list=[ListEntry("hidden")], is_blacklist=True)
        album_map = {}

        cols = get_active_collections(asset, bl, album_map)

        # Should be completely excluded since it's in an excluded smart album
        self.assertEqual(len(cols), 0)

    def test_asset_in_regular_album_but_excluded_smart_album_completely_excluded(self):
        """Test that assets in both regular albums and excluded smart albums are completely excluded."""
        from functional_components.file_extraction_engine.app.extraction_helpers import get_active_collections
        from functional_components.file_extraction_engine.domain.blacklist import Blacklist, ListEntry

        # Asset in regular album AND excluded smart album
        asset = self._create_test_asset(
            user_albums=["album-uuid-1"],
            smart_folders=["hidden"]
        )

        # Blacklist with hidden excluded
        bl = Blacklist(current_list=[ListEntry("hidden")], is_blacklist=True)
        album_map = {"album-uuid-1": "My Photos"}

        cols = get_active_collections(asset, bl, album_map)

        # Should be completely excluded despite being in regular album
        self.assertEqual(len(cols), 0)

    def test_asset_in_regular_album_and_non_excluded_smart_album_extracted(self):
        """Test that assets in regular albums and non-excluded smart albums are extracted."""
        from functional_components.file_extraction_engine.app.extraction_helpers import get_active_collections
        from functional_components.file_extraction_engine.domain.blacklist import Blacklist, ListEntry

        # Asset in regular album and non-excluded smart album
        asset = self._create_test_asset(
            user_albums=["album-uuid-1"],
            smart_folders=["selfies"]
        )

        # Blacklist with hidden excluded (but selfies not excluded)
        bl = Blacklist(current_list=[ListEntry("hidden")], is_blacklist=True)
        album_map = {"album-uuid-1": "My Photos"}

        cols = get_active_collections(asset, bl, album_map)
        titles = [c.title for c in cols]

        # Should be extracted to regular album and selfies smart album
        self.assertIn("My Photos", titles)
        self.assertIn("nua_selfies", titles)
        self.assertNotIn("nua_hidden", titles)

    def test_asset_in_multiple_excluded_smart_albums_completely_excluded(self):
        """Test that assets in multiple excluded smart albums are completely excluded."""
        from functional_components.file_extraction_engine.app.extraction_helpers import get_active_collections
        from functional_components.file_extraction_engine.domain.blacklist import Blacklist, ListEntry

        # Asset in multiple excluded smart albums
        asset = self._create_test_asset(
            user_albums=["album-uuid-1"],
            smart_folders=["hidden", "recently_deleted"]
        )

        # Blacklist with both excluded
        bl = Blacklist(current_list=[
            ListEntry("hidden"),
            ListEntry("recently_deleted")
        ], is_blacklist=True)
        album_map = {"album-uuid-1": "My Photos"}

        cols = get_active_collections(asset, bl, album_map)

        # Should be completely excluded
        self.assertEqual(len(cols), 0)

    def test_whitelist_mode_excluded_smart_albums_still_block_extraction(self):
        """Test that excluded smart albums block extraction even in whitelist mode."""
        from functional_components.file_extraction_engine.app.extraction_helpers import get_active_collections
        from functional_components.file_extraction_engine.domain.blacklist import Blacklist, ListEntry

        # Asset in whitelisted regular album but excluded smart album
        asset = self._create_test_asset(
            user_albums=["album-uuid-1"],
            smart_folders=["hidden"]
        )

        # Whitelist mode with regular album whitelisted, but hidden smart album excluded
        bl = Blacklist(current_list=[
            ListEntry("My Photos"),  # whitelisted
            ListEntry("hidden")      # excluded smart album
        ], is_blacklist=False)
        album_map = {"album-uuid-1": "My Photos"}

        cols = get_active_collections(asset, bl, album_map)

        # Should be excluded due to smart album, despite regular album being whitelisted
        self.assertEqual(len(cols), 0)


if __name__ == "__main__":
    unittest.main()
