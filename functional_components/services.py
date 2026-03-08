"""
Author: Noah Gregie
Date: 2026-02-19
Description: Contains the backup service and settings services for the main
    menu.
"""

from .backup_locator_and_validator.app.backup_model_builder import build_backup_model

from pathlib import Path

from .file_extraction_engine.domain.blacklist import ListEntry, Blacklist

from functional_components.file_extraction_engine.app.extract_files import (
    run_extraction_engine
)

import os

import tempfile, pathlib


def draw_progress_bar(progress, thread):
    import time
    import sys

    BAR_WIDTH = 70
    INDENT = "  "
    FILLED = "█"
    EMPTY  = "░"

    while thread.is_alive():
        pct    = min(progress.percent, 100)
        filled = int((pct / 100) * BAR_WIDTH)
        empty  = BAR_WIDTH - filled
        bar    = INDENT + FILLED * filled + EMPTY * empty + f"  {pct}%"
        print(f"\r{bar}", end="", flush=True)
        time.sleep(0.1)

    # Final bar reflecting actual completion
    pct    = min(progress.percent, 100)
    filled = int((pct / 100) * BAR_WIDTH)
    empty  = BAR_WIDTH - filled
    bar    = INDENT + FILLED * filled + EMPTY * empty + f"  {pct}%"
    print(f"\r{bar}", flush=True)


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
            f"- Device Name: ............... {device.name}\n"
            f"- Device Model: .............. {formatted_model}\n"
            f"- Device Submodel: ........... {submodel}\n"
            f"- iOS Version: ............... {device.ios_version}\n"
            f"Backup:\n"
            f"- Backup Encryption Status: .. {device_metadata.is_encrypted}\n"
            f"- Backup UUID/GUID: .......... {device_metadata.backup_uuid}\n"
            f"- Backup Date: ............... {formatted_backup_date}\n"
            f"Backup Contents:\n"
            f"- User Albums loaded: ........ {len(self.current_model.albums)}\n"
            f"- Unhidden Assets Loaded: .... {len(self.current_model.assets)}\n"
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
        self.current_list = set()
        self._original_full_list = set()
        self.is_blacklist_mode = True
        self.use_symlinks = True

    def toggle_symlinks(self):
        """Toggles the global symlink setting."""
        self.use_symlinks = not self.use_symlinks
        state = "ENABLED" if self.use_symlinks else "DISABLED"
        return f"Symlink creation is now {state}."    

    def get_engine_blacklist(self):
        """Returns a Blacklist object for the Extraction Engine to evaluate."""
        return Blacklist(
            current_list=list(self.current_list),
            is_blacklist=True  # Always treat as blacklist for engine.
        )
    
    def get_state(self):
        """
        Retrieves the current settings mode and the active list of albums.

        Returns:
            tuple: The mode as a string ("Blacklist" or "Whitelist"), and a
            comma-separated string of the currently selected albums.
        """
        mode = "Blacklist" if self.is_blacklist_mode else "Whitelist"

        if self.is_blacklist_mode:
            display_list = [entry.name for entry in self.current_list]
        
        # Subtracting blacklist from full list to get whitelist 
        else:   
            whitelist_objects = self._original_full_list - self.current_list    
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
        self.current_list.clear()
        self._original_full_list.clear()

        if not self.is_blacklist_mode:
            if not all_available_album_names:
                # Failsafe: Revert to blacklist if we don't have the albums to build the whitelist
                self.is_blacklist_mode = True
                return "[!] Error: Cannot create Whitelist without backup data."
     
            # Fill the blacklist with every album as an ListEntry object
            for name in all_available_album_names:
                clean = name.removesuffix(" [Smart Album]")
                entry = ListEntry(clean)
                self.current_list.add(entry)
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
        # Remove potential suffix indicating smart album.
        name = album_name.strip().removesuffix(" [Smart Album]")
        if not name:
            return False, "Album name cannot be empty."

        entry = ListEntry(name)

        if self.is_blacklist_mode:
            #  Add/Remove from the internal blacklist
            if entry in self.current_list:
                self.current_list.remove(entry)
                return True, f"Album '{entry.name}' removed from Blacklist."
            else:
                self.current_list.add(entry)
                return True, f"Album '{entry.name}' added to Blacklist."

        else:
            # Inverted logic: If it's in the working blacklist, "adding it to the whitelist" 
            # means we remove it from the working blacklist so the engine exports it.
            if entry in self.current_list:
                self.current_list.remove(entry)
                return True, f"Album '{entry.name}' added to Whitelist."
            else:
                # If they "remove" it from the whitelist, it goes back into the blacklist
                self.current_list.add(entry)
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
        entry = ListEntry(album_name)
        
        # If the object is inside the blacklist, it is not allowed. 
        return entry not in self.current_list


class DummyProgress:
    """A simple placeholder to catch the progress.percent updates from the engine."""
    def __init__(self):
        self.percent = 0


class ConversionService:
    """Manages conversion format settings."""

    SUPPORTED_CONVERSIONS = {
        "HEIC": "JPG",
        "MOV": "MP4",
    }

    def __init__(self):
        self.enabled = set()  # set of source extensions that are active

    def toggle(self, ext: str):
        ext = ext.upper()
        if ext in self.enabled:
            self.enabled.discard(ext)
            return f"Conversion {ext} → {self.SUPPORTED_CONVERSIONS[ext]} disabled."
        else:
            self.enabled.add(ext)
            return f"Conversion {ext} → {self.SUPPORTED_CONVERSIONS[ext]} enabled."

    def get_convert_type_dict(self) -> dict:
        """Returns the dict the extraction engine expects."""
        return {ext: self.SUPPORTED_CONVERSIONS[ext] for ext in self.enabled}
    

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
        if not backup_model or not hasattr(backup_model, 'albums'):
            return []

        result = []

        # User albums
        for album in backup_model.albums:
            entry = ListEntry(album.title)
            if entry.is_NUA:
                result.append(f"{album.title} [Smart Album]")
            else:
                result.append(album.title)

        # NUAs: scan assets to find which smart folders are actually present
        present_nuas = set()
        for asset in backup_model.assets:
            for nua in asset.relationships.smart_folders:
                present_nuas.add(nua)

        # Display names for each canonical NUA name
        NUA_DISPLAY = {
            "favorites": "favorites [Smart Album]",
            "hidden": "hidden [Smart Album]",
            "selfies": "selfies [Smart Album]",
            "recently_deleted": "recently_deleted [Smart Album]",
        }

        for nua in sorted(present_nuas):
            result.append(NUA_DISPLAY.get(nua, nua + " [Smart Album]"))

        return result
    
    def export_all(self, backup_model, destination_str, settings_service, conversion_service):
        """
        Export all function, based on psuedo code of extraction engine. subject to change.
        """
        if not backup_model:
            return False, "No backup loaded."

        try:
            import threading

            user_set_symlinks = settings_service.use_symlinks
            convert_type_dict = conversion_service.get_convert_type_dict()
            progress_tracker = DummyProgress()

            try:
                test = pathlib.Path(tempfile.mkdtemp()) / "test_link"
                test.symlink_to(pathlib.Path(tempfile.mkdtemp()))
                os_supports_symlinks = True
                test.unlink()
            except (OSError, NotImplementedError):
                os_supports_symlinks = False

            engine_error = []

            def run():
                try:
                    run_extraction_engine(
                        backup_model=backup_model,
                        blacklist=settings_service.get_engine_blacklist(),
                        output_root=Path(destination_str),
                        os_supports_symlinks=os_supports_symlinks,
                        user_set_symlinks=user_set_symlinks,
                        convert_type_dict=convert_type_dict,
                        progress=progress_tracker,
                    )
                except Exception as e:
                    import traceback
                    engine_error.append(traceback.format_exc())

            thread = threading.Thread(target=run, daemon=True)
            thread.start()

            # Draw progress bar while engine runs
            draw_progress_bar(progress_tracker, thread)

            thread.join()

            if engine_error:
                return False, f"Extraction Engine Error: {engine_error[0]}"

            return True, f"Export complete! Files saved to '{destination_str}'."

        except Exception as e:
            return False, f"Extraction Engine Error: {str(e)}"


    def export_single_album(self, backup_model, destination_str, album_name, settings_service, conversion_service):
        """Export a single specific album only."""
        if not backup_model:
            return False, "No backup loaded."

        from functional_components.file_extraction_engine.domain.blacklist import Blacklist, ListEntry

        # Build a whitelist containing only the requested album
        # Remove the suffix from the name
        is_nua = album_name.endswith(" [Smart Album]")
        clean_name = album_name.removesuffix(" [Smart Album]") if is_nua else album_name

        single_album_blacklist = Blacklist(
            current_list=[
                entry for entry in
                [ListEntry(album.title) for album in backup_model.albums
                    if album.title != album_name]
                + [ListEntry(nua) for nua in ["favorites", "hidden", "selfies", "recently_deleted"]
                    if nua != clean_name]
            ],
            is_blacklist=True
        )

        print(f"Target album: {album_name}")
        for album in backup_model.albums:
            if album.title == album_name:
                print(f"Album UUID: {album.album_uuid}")

        try:
            import threading
            user_set_symlinks = settings_service.use_symlinks
            convert_type_dict = conversion_service.get_convert_type_dict()
            progress_tracker = DummyProgress()

            try:
                test = pathlib.Path(tempfile.mkdtemp()) / "test_link"
                test.symlink_to(pathlib.Path(tempfile.mkdtemp()))
                os_supports_symlinks = True
                test.unlink()
            except (OSError, NotImplementedError):
                os_supports_symlinks = False

            engine_error = []

            def run():
                try:
                    run_extraction_engine(
                        backup_model=backup_model,
                        blacklist=single_album_blacklist,
                        output_root=Path(destination_str),
                        os_supports_symlinks=os_supports_symlinks,
                        user_set_symlinks=user_set_symlinks,
                        convert_type_dict=convert_type_dict,
                        progress=progress_tracker,
                        include_unassigned=False,
                    )
                except Exception as e:
                    import traceback
                    engine_error.append(traceback.format_exc())

            thread = threading.Thread(target=run, daemon=True)
            thread.start()
            draw_progress_bar(progress_tracker, thread)
            thread.join()

            if engine_error:
                return False, f"Extraction Engine Error: {engine_error[0]}"

            return True, f"Export complete! Files saved to '{destination_str}'."

        except Exception as e:
            return False, f"Extraction Engine Error: {str(e)}"
