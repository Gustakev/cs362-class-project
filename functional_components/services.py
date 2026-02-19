"""
Author: Noah Gregie
Date: 2026-02-19
Description: Contains the backup service and settings services for the main
    menu.
"""

from .backup_locator_and_validator.app.backup_model_builder import \
    build_backup_model

from pathlib import Path


class BackupService:
    def __init__(self):
        
        self.current_model = None

    def get_formatted_device_metadata(self):
        """
        Returns a pre-formatted string containing device info.
        """
        if not self.current_model:
            return "No backup loaded."

        # Access the domain object
        device = self.current_model.backup_metadata.source_device

        # Logic: Clean up the model string (e.g. "iPhone12,1" -> "iPhone 12,1")
        raw_model = device.model.split(",")[0]
        formatted_model = raw_model.replace("e", "e ")
        submodel = device.model.split(",")[1]

        # Return the string for the UI to use
        return (
            f"Device Name:     {device.name}\n"
            f"Device Model:    {formatted_model}\n"
            f"Device Submodel: {submodel}\n"
            f"iOS Version:     {device.ios_version}"
        )


    def attempt_load_backup(self, path_str):
        """
        Orchestrates the backup loading process.
        Returns: (Success Boolean, Message String)
        """
        if not path_str:
            return False, "No folder selected. Please try again."

        # Call the Backup Locator & Validator 
        result = build_backup_model(Path(path_str))

        if result.success:
            self.current_model = result.backup_model
            return True, "Backup loaded successfully!"
        else:
            return False, f"Error loading backup: {result.error}"


class SettingsService:
    def __init__(self):  
        self.selected_albums = set()
        self.is_blacklist_mode = True


def toggle_mode(self):
    """Switches between Blacklist and Whitelist mode."""
    self.is_blacklist_mode = not self.is_blacklist_mode
    mode_name = "Blacklist" if self.is_blacklist_mode else "Whitelist"
    return f"Mode switched to: {mode_name}"
