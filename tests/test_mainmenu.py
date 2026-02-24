"""
Author: Noah Gregie
Date: 2026-02-22
Description: UI Tests for the Command Line Interface menus using mocked user input.
"""

import unittest
from unittest.mock import patch
from cli_components.main_menu import (
    main_menu, 
    load_backup_menu, 
    export_all_menu,
    settings_menu
)

class TestMainMenuUI(unittest.TestCase):
    """Testing main menu loop"""
    @patch('builtins.print')
    @patch('builtins.input',side_effect = ['5'])
    def test_main_menu_exit(self, mock_input, mock_print):
        """Test that typing '5' successfully breaks the infinite loop and exits."""
        main_menu()
        
        # Check if the goodbye message was printed
        mock_print.assert_any_call("Thank you for using this program. Goodbye.")

    """Load backup menu check"""
    @patch('builtins.print')
    @patch('builtins.input', side_effect = ['2', '/fake/iphone/backup','3'])
    @patch('cli_components.main_menu.backup_service')

    def test_load_backup_manual_path(self, mock_backup_service, mock_input, mock_print):
        
        # Setup the mock service to pretend it succeeded
        mock_backup_service.attempt_load_backup.return_value = (True, "Mock Loaded")
        mock_backup_service.get_formatted_device_metadata.return_value = "Mock Data"

        # Run the menu
        load_backup_menu()

        # Did the UI actually hand the right string to the Application Layer
        mock_backup_service.attempt_load_backup.assert_called_with('/fake/iphone/backup')



    """Settings menu"""
    @patch ('builtins.print')
    @patch ('builtins.input', side_effect=['1','3'])
    @patch ('cli_components.main_menu.settings_service')
    @patch('cli_components.main_menu.backup_service')
    def test_settings_menu_toggle_mode(self, mock_backup, mock_settings, mock_input, mock_print):
        """Test that typing '1' in settings triggers the mode toggle in the service."""
        
        # Setup mock state for the menu to print
        mock_backup.current_model = "FakeModel"
        mock_settings.get_state.return_value = ("Blacklist", [])
        mock_settings.toggle_mode.return_value = "Switched to Whitelist"

        # Run the menu
        settings_menu()

        # Did the UI trigger the toggle function
        mock_settings.toggle_mode.assert_called_once()




if __name__ == '__main__':
    unittest.main()        