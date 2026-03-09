"""
Author: Noah Gregie
Date: 2026-02-22
Description: UI Tests for the Command Line Interface menus using mocked user input.
"""

import unittest
from unittest.mock import patch, MagicMock
from cli_components.main_menu import (
    main_menu,
    load_backup_menu,
    export_all_menu,
    settings_menu,
    get_export_destination,
    export_specific_menu,
    album_selection_submenu,
    gui_pick_folder,
    help_user,
    conversion_settings_menu,
    symlink_settings_menu,
    hidden_album_settings_menu,
)


class TestMainMenuUI(unittest.TestCase):
    """Testing main menu loop"""

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["9"])
    def test_main_menu_exit(self, mock_input, mock_print):
        """Test that typing '9' successfully breaks the infinite loop and exits."""
        # This safely catches the sys.exit() command so it stops the loop
        # without killing the test runner
        with self.assertRaises(SystemExit):
            main_menu()

        # Check if the goodbye message was printed
        mock_print.assert_any_call("Thank you for using this program. Goodbye.")

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["8"])
    @patch("cli_components.main_menu.restart_program")
    def test_main_menu_restart(self, mock_restart, mock_input, mock_print):
        """Selecting '8' should invoke restart and return from the menu."""
        # run the menu; should return normally without SystemExit
        main_menu()

        mock_restart.assert_called_once()
        # when restart_program is patched, its own print statement is skipped

    def test_restart_program_resets_state(self):
        """Calling restart_program should recreate all service objects."""
        # mutate the globals to something distinct
        from cli_components import main_menu as mm

        mm.backup_service.current_model = "dummy"
        mm.settings_service.use_symlinks = False

        old_backup = mm.backup_service
        old_settings = mm.settings_service
        old_export = mm.export_service
        old_conversion = mm.conversion_service

        mm.restart_program()

        self.assertIsNot(mm.backup_service, old_backup)
        self.assertIsNone(mm.backup_service.current_model)
        self.assertIsNot(mm.settings_service, old_settings)
        self.assertIsNot(mm.export_service, old_export)
        self.assertIsNot(mm.conversion_service, old_conversion)

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["1", "9"])
    @patch("cli_components.main_menu.load_backup_menu")
    def test_main_menu_routes_to_load_backup(
        self, mock_load_backup, mock_input, mock_print
    ):
        with self.assertRaises(SystemExit):
            main_menu()
        mock_load_backup.assert_called_once()

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["2", "9"])
    @patch("cli_components.main_menu.export_all_menu")
    def test_main_menu_routes_to_export_all(
        self, mock_export_all, mock_input, mock_print
    ):
        with self.assertRaises(SystemExit):
            main_menu()
        mock_export_all.assert_called_once()

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["3", "9"])
    @patch("cli_components.main_menu.export_specific_menu")
    def test_main_menu_routes_to_export_specific(
        self, mock_export_specific, mock_input, mock_print
    ):
        with self.assertRaises(SystemExit):
            main_menu()
        mock_export_specific.assert_called_once()

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["4", "9"])
    @patch("cli_components.main_menu.settings_menu")
    def test_main_menu_routes_to_settings(self, mock_settings, mock_input, mock_print):
        with self.assertRaises(SystemExit):
            main_menu()
        mock_settings.assert_called_once()

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["5", "9"])
    @patch("cli_components.main_menu.help_user")
    def test_main_menu_routes_to_help(self, mock_help, mock_input, mock_print):
        with self.assertRaises(SystemExit):
            main_menu()
        mock_help.assert_called_once()

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["6", "9"])
    @patch("cli_components.main_menu.webbrowser.open_new_tab")
    def test_main_menu_routes_to_bug_report(self, mock_browser, mock_input, mock_print):
        with self.assertRaises(SystemExit):
            main_menu()
        mock_browser.assert_called_once()

        args, _ = mock_browser.call_args
        self.assertIn("issues", args[0].lower())

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["7", "9"])
    @patch("cli_components.main_menu.feat_photo_caption")
    def test_main_menu_routes_to_photo_captioner(
        self, mock_captioner, mock_input, mock_print
    ):
        with self.assertRaises(SystemExit):
            main_menu()
        mock_captioner.assert_called_once()

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["invalid", "9"])
    def test_main_menu_handles_invalid_input(self, mock_input, mock_print):
        with self.assertRaises(SystemExit):
            main_menu()

        found = False
        for call in mock_print.call_args_list:
            if "Invalid input" in str(call):
                found = True
                break
        self.assertTrue(found, "The 'Invalid input' error message was not printed.")

    """Load backup menu check"""

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["2", "/fake/iphone/backup", "3"])
    @patch("cli_components.main_menu.backup_service")
    def test_load_backup_manual_path(self, mock_backup_service, mock_input, mock_print):
        # Setup the mock service to pretend it succeeded
        mock_backup_service.attempt_load_backup.return_value = (
            True,
            "Mock Loaded",
            None,
        )
        mock_backup_service.get_formatted_device_metadata.return_value = "Mock Data"

        # Run the menu
        load_backup_menu()

        # Did the UI actually hand the right string to the Application Layer
        mock_backup_service.attempt_load_backup.assert_called_with(
            "/fake/iphone/backup"
        )

    """Settings menu"""

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["1", "1", "3", "5"])
    @patch("cli_components.main_menu.export_service")
    @patch("cli_components.main_menu.settings_service")
    @patch("cli_components.main_menu.backup_service")
    def test_settings_menu_toggle_mode(
        self, mock_backup, mock_settings, mock_export, mock_input, mock_print
    ):
        """Test that typing '1' in settings triggers the mode toggle in the service.

        Input sequence:
          '1' -> enter Blacklist/Whitelist submenu from Settings
          '1' -> trigger toggle mode inside the submenu
          '3' -> go back from the submenu
          '5' -> go back from Settings
        """
        # Setup mock state for the menu to print
        mock_backup.current_model = "FakeModel"
        mock_settings.get_state.return_value = ("Blacklist", [])
        mock_settings.toggle_mode.return_value = "Switched to Whitelist"
        mock_export.get_album_list.return_value = ["Album A", "Album B"]

        # Run the menu
        settings_menu()

        # Did the UI trigger the toggle function
        mock_settings.toggle_mode.assert_called_once()

    @patch("builtins.print")
    @patch("cli_components.main_menu.backup_service")
    def test_disabled_settings_menu(self, mock_backup, mock_print):
        """Test that settings menu blocks access when no backup is loaded."""
        # Setup mock state - no backup loaded
        mock_backup.current_model = None

        # Run the menu - should return immediately without prompting
        settings_menu()

        # Did the UI display the correct error message
        mock_print.assert_any_call(
            "\033[31m"
            + "\n[!] Error: You must load a backup before changing settings."
            + "\033[0m"
        )

    """Testing destination helper with a manual path entry"""

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["2", "/my/custom/export/path", "y"])
    def test_get_export_destination_manual(self, mock_input, mock_print):
        result = get_export_destination("Camera Roll")

        self.assertEqual(result, "/my/custom/export/path")
        mock_print.assert_any_call(
            "\nHow would you like to select the destination folder for Camera Roll?"
        )

    """Testing that export menu rejects users if backup is not loaded"""

    @patch("builtins.print")
    @patch("cli_components.main_menu.backup_service")
    def test_export_all_menu_blocked(self, mock_backup_service, mock_print):
        mock_backup_service.current_model = None

        export_all_menu()

        # Check the exact screen output
        mock_print.assert_any_call(
            "\033[31m" + "[!] Error: No backup loaded. Please load a backup first."
            "\033[31m"
        )

    """Testing exporting a specific album"""

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["Favorites"])
    @patch(
        "cli_components.main_menu.get_export_destination",
        return_value="/fake/export/path",
    )
    @patch("cli_components.main_menu.export_service")
    @patch("cli_components.main_menu.backup_service")
    def test_export_specific_menu_flow(
        self, mock_backup, mock_export, mock_get_dest, mock_input, mock_print
    ):
        # Fake the loaded backup and the available albums list
        mock_backup.current_model = "FakeModelLoaded"
        mock_export.get_album_list.return_value = ["Recents", "Favorites", "Hidden"]
        mock_export.export_single_album.return_value = (True, "Export complete!")

        export_specific_menu()

        mock_get_dest.assert_called_once_with("'Favorites'")
        mock_export.export_single_album.assert_called_once()

    """Adding an album to the Blacklist"""

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["1", "Instagram", "cancel", "3"])
    @patch("cli_components.main_menu.settings_service")
    @patch("cli_components.main_menu.export_service")
    @patch("cli_components.main_menu.backup_service")
    def test_album_selection_manual_entry(
        self, mock_backup, mock_export, mock_settings, mock_input, mock_print
    ):
        # Setup
        mock_backup.current_model = "FakeModelLoaded"
        mock_export.get_album_list.return_value = ["Instagram", "WhatsApp"]
        mock_settings.get_state.return_value = ("Blacklist", "None")
        mock_settings.toggle_album.return_value = (True, "Album 'Instagram' added.")

        album_selection_submenu()

        # Verify the settings service was successfully handed the targeted string
        mock_settings.toggle_album.assert_called_once_with("Instagram")

    @patch("cli_components.main_menu.filedialog.askdirectory")
    @patch("cli_components.main_menu.tk.Tk")
    def test_gui_pick_folder(self, mock_tk, mock_askdirectory):
        """Test that the GUI picker returns the mocked path cleanly."""
        mock_askdirectory.return_value = "/mocked/folder/path"

        result = gui_pick_folder()

        self.assertEqual(result, "/mocked/folder/path")
        mock_askdirectory.assert_called_once()

    @patch("cli_components.main_menu.webbrowser.open_new_tab")
    @patch("builtins.input", side_effect=["1", "2", "3"])
    def test_help_user(self, mock_input, mock_open_tab):
        """Test the help menu navigation and browser opening."""
        help_user()

        # Since the user typed 1 and 2, the browser should have opened twice
        self.assertEqual(mock_open_tab.call_count, 2)

        # Check that it opened the correct user doc URL on the first try
        args, kwargs = mock_open_tab.call_args_list[0]
        self.assertIn("iExtract-User-Documentation.md", args[0])

    # Testing get_export_ destination

    @patch("builtins.input", side_effect=["2", "/manual/test/path", "y"])
    def test_get_export_dest_manual_confirm(self, mock_input):
        """Test entering a manual path and confirming with 'y'."""
        result = get_export_destination("test item")
        self.assertEqual(result, "/manual/test/path")

    @patch("builtins.input", side_effect=["3"])
    def test_get_export_dest_cancel_immediately(self, mock_input):
        """Test picking option 3 to cancel instantly."""
        result = get_export_destination("test item")
        self.assertIsNone(result)

    @patch("cli_components.main_menu.gui_pick_folder", return_value="/gui/path")
    @patch("builtins.input", side_effect=["1", "n"])
    def test_get_export_dest_gui_then_decline(self, mock_input, mock_gui):
        """Test picking the GUI option, getting a path, but declining the confirmation."""
        result = get_export_destination("test item")
        self.assertIsNone(result)
        mock_gui.assert_called_once()

    #  CONVERSION SETTINGS MENU
    @patch("builtins.input", side_effect=["1", "99", "3"])
    @patch("cli_components.main_menu.conversion_service")
    def test_conversion_settings_menu(self, mock_conv_service, mock_input):
        """
        Tests:
        - Toggle first option (HEIC)
        - Invalid choice (99)
        - Exit (3)
        """
        # Mock the service response
        mock_conv_service.enabled = set()
        mock_conv_service.toggle.return_value = "HEIC enabled"

        conversion_settings_menu()

        # Verify toggle was called with "HEIC" (first key in dict)
        mock_conv_service.toggle.assert_called_with("HEIC")
        self.assertEqual(mock_input.call_count, 3)

    # SYMLINK SETTINGS MENU
    @patch("builtins.input", side_effect=["1", "invalid", "2"])
    @patch("cli_components.main_menu.settings_service")
    def test_symlink_settings_menu(self, mock_settings, mock_input):
        """
        Tests:
        - Toggle Symlinks
        - Invalid input string
        - Exit (2)
        """
        mock_settings.use_symlinks = True
        mock_settings.toggle_symlinks.return_value = "Symlinks DISABLED"

        symlink_settings_menu()

        mock_settings.toggle_symlinks.assert_called_once()
        self.assertEqual(mock_input.call_count, 3)

    # HIDDEN ALBUM SETTINGS MENU
    @patch("builtins.input", side_effect=["1", "3", "2"])
    @patch("cli_components.main_menu.settings_service")
    def test_hidden_album_settings_menu(self, mock_settings, mock_input):
        """
        Tests:
        - Toggle Hidden Album
        - Invalid number (3)
        - Exit (2)
        """
        mock_settings.exclude_hidden_album = False
        mock_settings.toggle_exclude_hidden_album.return_value = (
            "Hidden Exclusion ENABLED"
        )

        hidden_album_settings_menu()

        mock_settings.toggle_exclude_hidden_album.assert_called_once()
        self.assertEqual(mock_input.call_count, 3)


if __name__ == "__main__":
    unittest.main()
