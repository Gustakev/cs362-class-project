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
    settings_menu,
    get_export_destination,
    export_specific_menu,
    album_selection_submenu
)


class TestMainMenuUI(unittest.TestCase):
    """Testing main menu loop"""
    
    """Testing main menu loop"""
    @patch('builtins.print')
    @patch('builtins.input',side_effect = ['9'])
    def test_main_menu_exit(self, mock_input, mock_print):
        """Test that typing '9' successfully breaks the infinite loop and exits."""
        # This safely catches the sys.exit() command so it stops the loop without killing the test runner
        with self.assertRaises(SystemExit):
            main_menu()
        
        # Check if the goodbye message was printed
        mock_print.assert_any_call("Thank you for using this program. Goodbye.")

    @patch('builtins.print')
    @patch('builtins.input', side_effect=['1', '9'])
    @patch('cli_components.main_menu.load_backup_menu')
    def test_main_menu_routes_to_load_backup(self, mock_load_backup, mock_input, mock_print):
        with self.assertRaises(SystemExit):
            main_menu()
        mock_load_backup.assert_called_once()

    @patch('builtins.print')
    @patch('builtins.input', side_effect=['2', '9'])
    @patch('cli_components.main_menu.export_all_menu')
    def test_main_menu_routes_to_export_all(self, mock_export_all, mock_input, mock_print):
        with self.assertRaises(SystemExit):
            main_menu()
        mock_export_all.assert_called_once()

    @patch('builtins.print')
    @patch('builtins.input', side_effect=['3', '9'])
    @patch('cli_components.main_menu.export_specific_menu')
    def test_main_menu_routes_to_export_specific(self, mock_export_specific, mock_input, mock_print):
        with self.assertRaises(SystemExit):
            main_menu()
        mock_export_specific.assert_called_once()

    @patch('builtins.print')
    @patch('builtins.input', side_effect=['4', '9'])
    @patch('cli_components.main_menu.settings_menu')
    def test_main_menu_routes_to_settings(self, mock_settings, mock_input, mock_print):
        with self.assertRaises(SystemExit):
            main_menu()
        mock_settings.assert_called_once()


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

    @patch ('builtins.print')
    @patch ('builtins.input', side_effect=['1','3'])
    @patch ('cli_components.main_menu.settings_service')
    @patch('cli_components.main_menu.backup_service')
    def test_disabled_settings_menu(self, mock_backup, mock_settings, mock_input, mock_print):
        """Test that typing '1' in settings triggers the mode toggle in the service."""
        
        # Setup mock state for the menu to print
        mock_backup.current_model = None
        mock_settings.get_state.return_value = ("Blacklist", [])
        mock_settings.toggle_mode.return_value = "Switched to Whitelist"

        # Run the menu
        settings_menu()

        # Did the UI trigger the toggle function
        mock_print.assert_any_call("\n[!] Error: You must load a backup before changing settings.")



    """Testing destination helper with a manual path entry"""
    @patch('builtins.print')
    @patch('builtins.input', side_effect=['2', '/my/custom/export/path', 'y'])
    def test_get_export_destination_manual(self, mock_input, mock_print):
    
        
        result = get_export_destination("Camera Roll")
        
        self.assertEqual(result, '/my/custom/export/path')
        mock_print.assert_any_call("\nHow would you like to select the destination folder for Camera Roll?")


    """Testing that export menu rejects users if backup is not loaded"""
    @patch('builtins.print')
    @patch('cli_components.main_menu.backup_service')
    def test_export_all_menu_blocked(self, mock_backup_service, mock_print):
    
       
        mock_backup_service.current_model = None 
        
        
        export_all_menu()
        
        # Check the exact screen output
        mock_print.assert_any_call("[!] Error: No backup loaded. Please load a backup first.")


    """Testing exporting a specific album"""
    @patch('builtins.print')
    @patch('builtins.input', side_effect=['Favorites'])
    @patch('cli_components.main_menu.get_export_destination', return_value='/fake/export/path')
    @patch('cli_components.main_menu.export_service')
    @patch('cli_components.main_menu.backup_service')
    def test_export_specific_menu_flow(self, mock_backup, mock_export, mock_get_dest, mock_input, mock_print):
       
       
        
       # Fake the loaded backup and the available albums list
        mock_backup.current_model = "FakeModelLoaded"
        mock_export.get_album_list.return_value = ["Recents", "Favorites", "Hidden"]
        
        export_specific_menu()
        
        # Ensure the helper was triggered with the exact formatted string
        mock_get_dest.assert_called_once_with("'Favorites'")


    """Adding a album to the Blacklist"""
    @patch('builtins.print')
    @patch('builtins.input', side_effect=['1', 'Instagram', 'done', '3'])
    @patch('cli_components.main_menu.settings_service')
    @patch('cli_components.main_menu.export_service')
    @patch('cli_components.main_menu.backup_service')
    def test_album_selection_manual_entry(self, mock_backup, mock_export, mock_settings, mock_input, mock_print):
        
        
        #  Setup
        mock_backup.current_model = "FakeModelLoaded"
        mock_export.get_album_list.return_value = ["Instagram", "WhatsApp"]
        mock_settings.get_state.return_value = ("Blacklist", "None")
        mock_settings.toggle_album.return_value = (True, "Album 'Instagram' added.")
        
        album_selection_submenu()
        
        # Verify the settings service was successfully handed the targeted string
        mock_settings.toggle_album.assert_called_once_with("Instagram")


    

if __name__ == '__main__':
    unittest.main()        