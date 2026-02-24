"""
Author: Noah Gregie
Date: 2026-02-19
Description: Contains the backup service and settings services for the main
    menu.
"""

from .backup_locator_and_validator.app.backup_model_builder import build_backup_model

from pathlib import Path


class BackupService:
    """
    Manages the state of the loaded iPhone backup in memory.
    Serves as the bridge between the UI and the backup model builder.
    """

    def __init__(self):
        # Holds the fully constructed BackupModel object once successfully loaded.
        self.current_model = None

    def get_formatted_device_metadata(self):
        """
        Retrieves and formats device and backup metadata for display in the UI.

        Returns:
            str: A formatted string containing device details, or an error
            message if no backup is currently loaded in memory.
        """
        if not self.current_model:
            return "No backup loaded."

        # Access the domain object
        device = self.current_model.backup_metadata.source_device

        # Logic: Clean up the model string (e.g. "iPhone12,1" -> "iPhone 12,1")
        raw_model = device.model.split(",")[0]
        formatted_model = raw_model.replace("e", "e ")
        submodel = device.model.split(",")[1]

        # Access the backup_metadata fields regarding backup info specifically
        device_metadata = self.current_model.backup_metadata

        # Logic: Clean up the formatting of the backup date.
        formatted_backup_date = device_metadata.backup_date
        formatted_backup_date = formatted_backup_date.replace("T", " at (24H Time): ")

        # Return the string for the UI to use
        return (
            f"Device:\n"
            f"- Device Name: ............ {device.name}\n"
            f"- Device Model: ........... {formatted_model}\n"
            f"- Device Submodel: ........ {submodel}\n"
            f"- iOS Version: ............ {device.ios_version}\n"
            f"Backup:\n"
            f"- Backup Encryption Status: {device_metadata.is_encrypted}\n"
            f"- Backup UUID/GUID: ....... {device_metadata.backup_uuid}\n"
            f"- Backup Date: ............ {formatted_backup_date}"
        )

    def attempt_load_backup(self, path_str):
        """
        Orchestrates the backup loading process.

        Args:
            path_str (str): The file path to the selected iPhone backup directory.
        Returns:
            tuple: A boolean indicating success, and a corresponding message string.
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
    """
    Manages the logic for whitelisting and blacklisting albums.
    Maintains the current configuration state for the export phase.
    """

    def __init__(self):
        self.selected_albums = set()
        self.is_blacklist_mode = True

    def get_state(self):
        """
        Retrieves the current settings mode and the active list of albums.

        Returns:
            tuple: The mode as a string ("Blacklist" or "Whitelist"), and a
            comma-separated string of the currently selected albums.
        """
        mode = "Blacklist" if self.is_blacklist_mode else "Whitelist"
        album_list = ", ".join(self.selected_albums) if self.selected_albums else "None"
        return mode, album_list

    def toggle_mode(self):
        """
        Switches the application between Blacklist and Whitelist mode.
        Automatically clears the current album selection to prevent logic bleed.

        Returns:
            str: A formatted string confirming the mode switch.
        """
        self.is_blacklist_mode = not self.is_blacklist_mode
        self.selected_albums.clear()
        mode_name = "Blacklist" if self.is_blacklist_mode else "Whitelist"
        return f"Mode switched to: {mode_name}"

    def toggle_album(self, album_name):
        """
        Adds or removes an album from the active selection set.

        Args:
            album_name (str): The exact string name of the album to toggle.

        Returns:
            tuple: A boolean indicating success (False if empty), and a
            message string confirming the action taken.
        """
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
        """
        Determines if a specific album is eligible for export based on the
        current Blacklist/Whitelist configuration.

        Args:
            album_name (str): The string name of the album being checked.

        Returns:
            bool: True if the album should be exported, False otherwise.
        """
        if self.is_blacklist_mode:
            return album_name not in self.selected_albums
        else:
            return album_name in self.selected_albums


class ExportService:
    """
    Handles the orchestration of extracting media from the backup and
    writing it to the local destination path.
    """

    def get_album_list(self, backup_model):
        """
        Retrieves a list of all available albums contained within the parsed backup.

        Args:
            backup_model: The fully constructed SourceDevice model object.

        Returns:
            list: A list of string album names.
        """
        # TODO: Return actual list from backup_model.albums
        return ["Recents", "Favorites", "Instagram", "WhatsApp", "Hidden"]
