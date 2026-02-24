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

    """Manages whitelisting and blacklsiting of albums for export."""

    def __init__(self):  
        self.selected_albums = set()
        self.is_blacklist_mode = True

    def get_state(self):
        """Returns the current settings state."""
        mode = "Blacklist" if self.is_blacklist_mode else "Whitelist"
        album_list = ", ".join(self.selected_albums) if self.selected_albums else "None"
        return mode, album_list

    def toggle_mode(self):
        """Switches between Blacklist and Whitelist mode."""
        self.is_blacklist_mode = not self.is_blacklist_mode
        self.selected_albums.clear()
        mode_name = "Blacklist" if self.is_blacklist_mode else "Whitelist"
        return f"Mode switched to: {mode_name}"
    
    def toggle_album(self, album_name):
        """Adds or removes an album from the selection based on current mode."""
        name = album_name.strip()
        if not name:
            return False, "Album name cannot be empty."
        if name in self.selected_albums:
            self.selected_albums.remove(name)
            return True, f"Album '{name}' removed from selection."
        else:
            self.selected_albums.add(name)
            return True, f"Album '{name}' added to selection."
        

    def is_album_allowed(self, album_name):
        """Determines if an album should be exported based on current settings."""
        if self.is_blacklist_mode:
            return album_name not in self.selected_albums
        else:
            return album_name in self.selected_albums


class ExportService:
   def get_album_list(self, backup_model):
        # TODO: Return actual list from backup_model.albums
        return ["Recents", "Favorites", "Instagram", "WhatsApp", "Hidden"]