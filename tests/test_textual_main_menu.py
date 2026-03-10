"""
Author: Noah Gregie
Date: 2026-03-01
Description: UI Tests for the Textual GUI interface using async test to simulate a user
pressing buttons.
"""

import unittest
from unittest.mock import patch

# Adjust this import path if needed to match your project structure
from cli_components.textual_main_menu import iExtractApp


class TestTextualUI(unittest.IsolatedAsyncioTestCase):

    async def test_initial_startup_state(self):
        """Test that the app starts with the main menu visible and submenus hidden."""
        app = iExtractApp()

        async with app.run_test() as pilot:
            # Main menu should be visible
            self.assertFalse(app.query_one("#main_menu").has_class("hidden"))

            # Submenus should be hidden
            self.assertTrue(app.query_one("#backup_options").has_class("hidden"))
            self.assertTrue(app.query_one("#settings_options").has_class("hidden"))

    async def test_navigation_to_load_backup(self):
        """Test clicking the load backup button swaps the menus."""
        app = iExtractApp()
        async with app.run_test() as pilot:
            await pilot.click("#btn_load")
            await pilot.pause()

            # Main menu should now be hidden, and backup options visible
            self.assertTrue(app.query_one("#main_menu").has_class("hidden"))
            self.assertFalse(app.query_one("#backup_options").has_class("hidden"))

            # The system log should have a new entry
            log_text = app.query_one("#log_window").lines[-1]
            self.assertIn("[MENU] Select load method...", log_text)

    async def test_navigation_back_button(self):
        """Test going into a menu and clicking 'Go Back'."""
        app = iExtractApp()

        app.backup_service.current_model = "MockedBackupData"

        async with app.run_test() as pilot:
            # Go to settings
            await pilot.click("#btn_settings")
            await pilot.pause()
            self.assertFalse(app.query_one("#settings_options").has_class("hidden"))

            # Click 'Go Back'
            await pilot.click("#btn_back_settings")
            await pilot.pause()

            # Verify we are back at the main menu
            self.assertTrue(app.query_one("#settings_options").has_class("hidden"))
            self.assertFalse(app.query_one("#main_menu").has_class("hidden"))

    async def test_exit_button(self):
        """Test that the exit button successfully calls the app's exit routine."""
        app = iExtractApp()

        async with app.run_test(size=(120, 50)) as pilot:

            with patch.object(app, "exit") as mock_exit:
                await pilot.click("#btn_exit")
                await pilot.pause()

                # Verify the exit function was triggered
                mock_exit.assert_called_once()

    async def test_navigation_to_help(self):
        """Test clicking the Help button opens the help submenu."""
        app = iExtractApp()
        async with app.run_test(size=(120, 50)) as pilot:
            await pilot.click("#btn_help")
            await pilot.pause()

            # Verify Main Menu is hidden and Help Options are visible
            self.assertTrue(app.query_one("#main_menu").has_class("hidden"))
            self.assertFalse(app.query_one("#help_options").has_class("hidden"))

    @patch("webbrowser.open_new_tab")
    async def test_report_bug_button(self, mock_browser):
        """Test that the Bug Report button opens the correct GitHub URL."""
        app = iExtractApp()
        async with app.run_test(size=(120, 50)) as pilot:
            await pilot.click("#btn_bug")
            await pilot.pause()

            # Verify the browser was called with the issues URL
            mock_browser.assert_called_once()
            args, _ = mock_browser.call_args
            self.assertIn("issues", args[0])

    async def test_navigation_to_photo_beta(self):
        """Test clicking the Photo Descriptor button swaps the menus."""
        app = iExtractApp()
        async with app.run_test(size=(120, 50)) as pilot:
            await pilot.click("#btn_photo_beta")
            await pilot.pause()

            self.assertTrue(app.query_one("#main_menu").has_class("hidden"))
            self.assertFalse(app.query_one("#photo_beta_options").has_class("hidden"))

    async def test_export_all_error_no_backup(self):
        """Test that Export All shows an error if no backup is loaded."""
        app = iExtractApp()

        app.backup_service.current_model = None

        async with app.run_test(size=(120, 50)) as pilot:
            await pilot.click("#btn_export_all")
            await pilot.pause()

            # Check the log for the specific error message
            log_text = app.query_one("#log_window").lines[-1]
            self.assertIn("No backup loaded", log_text)


if __name__ == "__main__":
    unittest.main()
