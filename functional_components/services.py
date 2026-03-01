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
                

class listEntry:
    """
    Represents an album or collection as a filterable object.
    Automatically identifies Non-User-Albums (NUAs).
    """
    # Define standard NUAs for special extraction engine handling
    NUAS = {"Favorites", "Hidden", "Selfies", "Recently Deleted"}

    def __init__(self, name: str):
        self.name = name.strip()
        self.is_nua = self.name in self.NUAS

    def __eq__(self, other):
        """Allows Python to compare two AlbumFilterEntry objects by name."""
        if isinstance(other, listEntry):
            return self.name == other.name
        return False

    def __hash__(self):
        """Allows AlbumFilterEntry objects to be stored in Sets for difference calculations."""
        return hash(self.name)




class SettingsService:
    """
    Manages the logic for whitelisting and blacklisting albums.
    Maintains the current configuration state for the export phase.
    """

    def __init__(self):
        self._working_blacklist = set()
        self._original_full_list = set()
        self.is_blacklist_mode = True


    def get_engine_blacklist(self):
        """Returns the final blacklist for the Extraction Engine to evaluate.
        """
        return self._working_blacklist    

    def get_state(self):
        """
        Retrieves the current settings mode and the active list of albums.

        Returns:
            tuple: The mode as a string ("Blacklist" or "Whitelist"), and a
            comma-separated string of the currently selected albums.
        """
        mode = "Blacklist" if self.is_blacklist_mode else "Whitelist"

        if self.is_blacklist_mode:
            display_list = [entry.name for entry in self._working_blacklist]
        
        # Subtracting blacklist from full list to get whitelist 
        else:   
            whitelist_objects = self._original_full_list - self._working_blacklist    
            display_list = [entry.name for entry in whitelist_objects]


        album_string = ", ".join(display_list) if display_list else "None"
        return mode, album_string    

    def toggle_mode(self,all_available_album_names=None):
        """
        Switches the application between Blacklist and Whitelist mode.
        Automatically clears the current album selection to prevent logic bleed.

        Returns:
            str: A formatted string confirming the mode switch.
        """
        self.is_blacklist_mode = not self.is_blacklist_mode
        self._working_blacklist.clear()
        self._original_full_list.clear()

        if not self.is_blacklist_mode:
            if not all_available_album_names:
                # Failsafe: Revert to blacklist if we don't have the albums to build the whitelist
                self.is_blacklist_mode = True
                return "[!] Error: Cannot create Whitelist without backup data."
     
        # Fill the blacklist with every album as an ListEntry object
            for name in all_available_album_names:
                entry = listEntry(name)
                self._working_blacklist.add(entry)
                self._original_full_list.add(entry)

            return "Mode switched to: Whitelist (List cleared. Select albums to ALLOW.)"
        
        return "Mode switched to: Blacklist (List cleared. Select albums to BLOCK.)"
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

        entry = listEntry(album_name)    

        if self.is_blacklist_mode:
            #  Add/Remove from the internal blacklist
            if entry in self._working_blacklist:
                self._working_blacklist.remove(entry)
                return True, f"Album '{entry.name}' removed from Blacklist."
            else:
                self._working_blacklist.add(entry)
                return True, f"Album '{entry.name}' added to Blacklist."

        else:
            # Inverted logic: If it's in the working blacklist, "adding it to the whitelist" 
            # means we remove it from the working blacklist so the engine exports it.
            if entry in self._working_blacklist:
                self._working_blacklist.remove(entry)
                return True, f"Album '{entry.name}' added to Whitelist."
            else:
                # If they "remove" it from the whitelist, it goes back into the blacklist
                self._working_blacklist.add(entry)
                return True, f"Album '{entry.name}' removed from Whitelist."


    def is_album_allowed(self, album_name):
        """
        Determines if a specific album is eligible for export based on the
        current Blacklist/Whitelist configuration.

        Args:
            album_name (str): The string name of the album being checked.

        Returns:
            bool: True if the album should be exported, False otherwise.
        """
        entry = listEntry(album_name)
        
        # If the object is inside the blacklist, it is not allowed. 
        return entry not in self._working_blacklist


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
