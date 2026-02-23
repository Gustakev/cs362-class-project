"""
Author: Kevin Gustafson
Date: 2026-01-29
Program Description: Command line interface for iExtract.
"""

import sys

import tkinter as tk
from tkinter import filedialog

from pathlib import Path

from functional_components.services import BackupService, SettingsService, ExportService

backup_service = BackupService()
settings_service = SettingsService()
export_service =  ExportService()

def gui_pick_folder():
    """
    Opens a GUI folder picker dialog and returns the selected folder path.

    Returns:
        str | None: The selected folder path, or None if GUI is unavailable.
    """
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        root.update()

        folder = filedialog.askdirectory(title="Select a folder")
        return folder

    except tk.TclError:
        print(
            "Error: GUI folder selection is not available on this system.",
            file=sys.stderr
        )
        return None


def print_device_metadata():
    """Prints device metadata in a nice format."""
    device_data = backup_service.get_formatted_device_metadata()

    print(device_data)


def load_backup_menu():
    """
    Submenu for choosing how to pick the backup folder.
    """

    while True:
        print(
            "*** Instructions: Enter a number corresponding to the choices "
            "below. ***\n"
        )
        print("1. Load iPhone Backup Folder Via GUI")
        print("2. Load iPhone Backup Folder By Entering File Path")
        print("3. Go Back")

        folder_picker_method = input("\nChoose an option: ")
        selected_folder = None

        if folder_picker_method == "1":
            selected_folder = gui_pick_folder()
            print("")
            print("You chose:", selected_folder)

        elif folder_picker_method == "2":
            print("")
            selected_folder = input("Enter the path to your iPhone backup " \
                "folder: ")
            print("")
            print("You chose:", selected_folder)
    
        elif folder_picker_method == "3":
            print("\nGoing back...\n")
            return

        else:
            print(
                "\nError: Invalid input. Choose one of the displayed options.",
                file=sys.stderr
            )
            print("")
            continue

        success, message = backup_service.attempt_load_backup(selected_folder)

        if success:
            print(f"\n{message}")
                # Fetch formatted metadata from services.py and print
            print(backup_service.get_formatted_device_metadata())
            print("")
            return
        else:
            print(f"\n{message}\n")

def main_menu():
    """
    Main program command-line interface loop.
    """
    while True:
        print(
            "\n========================= iExtract Main Menu ============="
            "============"
        )
        print(
            "\n** Instructions: Enter a number corresponding to the "
            "choices below. **\n"
        )
        print("1. Load iPhone Backup Folder")
        print("2. Export All Camera Roll Media")
        print("3. Export Specific Camera Roll Media")
        print("4. Settings")
        print("5. Exit")

        main_menu_choice = input("\nChoose an option: ")
        print("")

        if main_menu_choice == "1":
            load_backup_menu()
        elif main_menu_choice == "2":
            export_all_menu()
        elif main_menu_choice == "3":
            export_specific_menu()
        elif main_menu_choice == "4":
            settings_menu()
        elif main_menu_choice == "5":
            print("Thank you for using this program. Goodbye.")
            return
        else:
            print(
                "Error: Invalid input. Choose one of the displayed options.",
                file=sys.stderr
            )


def backup_menu():
    """Placeholder for backup menu."""
    print("")


def export_all_menu():
    """Exports all albums from the backup """
    print("\n--- EXPORT ALL ---")
    if not backup_service.current_model:
        print("[!] Error: No backup loaded. Please load a backup first.")
        return
    
    dest_path = input("Enter destination folder path: ").strip()
    if not dest_path:
        print("Export cancelled.")
        return
    
    print(f"Preparing to export all albums to: {dest_path}")
    confirm = input("Proceed? (y/n): ")
    if confirm.lower() != 'y':
        return
    
    """Here is where the function would call the export all function"""


def export_specific_menu():
    print("\n--- EXPORT SPECIFIC ALBUM ---")

    if not backup_service.current_model:
        print("[!] Error: No backup loaded. Please load a backup first.")
        return
    
    available_albums = export_service.get_album_list(backup_service.current_model)


    if not available_albums:
        print("[!] No albums found in backup.")
        return
    
    print(f"\nFound {len(available_albums)} albums:")
    """For loop printing out available albums with numbers for selection"""

    choice = input("\nEnter the number of the album you want to export: ")
    """Input validation for choice"""
    
    dest_path = input(f"Enter destination for 'selected_album': ")

    """Export the album that the user selected"""""
def settings_menu():
    
    while True:
        # Get data from Service
        mode, album_list = settings_service.get_state()

        print("\n--- SETTINGS ---")
        print(f"Mode: {mode}")
        print(f"List: [{album_list}]")
        print("1. Switch Mode (Whitelist/Blacklist)")
        print("2. Add/Remove Album")
        print("3. Back")

        choice = input("Select: ")

        if choice == "1":
            print(settings_service.toggle_mode())
        elif choice == "2":
            name = input("Album Name: ")
            success, msg = settings_service.toggle_album(name)
            print(msg)
        elif choice == "3":
            return

       


def input_validation():
    """Placeholder for input validation."""
    print("")


def progress_display():
    """Placeholder for progress display."""
    print("")


def error_display():
    """Placeholder for error display."""
    print("")


def main():
    """
    Program entrypoint.
    """
    main_menu()


if __name__ == "__main__":
    main()
