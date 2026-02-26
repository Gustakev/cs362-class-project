"""
Author: Kevin Gustafson (Brendon Wong worked on 2026-02-26)
Date: 2026-01-29
Program Description: Command line interface for iExtract.
"""

import sys

import tkinter as tk
from tkinter import filedialog

import webbrowser

from pathlib import Path

from functional_components.services import BackupService, SettingsService, ExportService
#from functional_components.photo_captioner import get_caption

backup_service = BackupService()
settings_service = SettingsService()
export_service = ExportService()


def gui_pick_folder():
    """
    Opens a GUI folder picker dialog and returns the selected folder path.

    Returns:
        str | None: The selected folder path, or None if GUI is unavailable.
    """
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        root.update()

        folder = filedialog.askdirectory(title="Select a folder")
        return folder

    except tk.TclError:
        print(
            "Error: GUI folder selection is not available on this system.",
            file=sys.stderr,
        )
        return None


def print_device_metadata():
    """
    Prints device metadata in a nice format.

    """
    device_data = backup_service.get_formatted_device_metadata()

    print(device_data)


def load_backup_menu():
    """
    Handles the user interaction for locating and loading an iPhone backup folder.
    Loops continuously until a valid path is provided or the user cancels.
    """

    while True:
        print(
            "** Instructions: Enter a number corresponding to the choices "
            "below. **\n"
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
            selected_folder = input("Enter the path to your iPhone backup " "folder: ")
            print("")
            print("You chose:", selected_folder)

        elif folder_picker_method == "3":
            print("\nGoing back...\n")
            return

        else:
            print(
                "\nError: Invalid input. Choose one of the displayed options.",
                file=sys.stderr,
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
        print("5. Help")
        print("6. Report Bug")
        print("7. Photo Descriptor (Beta Demo)")
        print("8. Restart")
        print("9. Exit")

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
            help_user()
        elif main_menu_choice == "6":
            report_bug()
        elif main_menu_choice == "7":
            # TODO
            # Needs to get user input still
            get_caption(...)
        elif main_menu_choice == "8":
            print("Error w/Restart Feature: Feature not yet implemented.")
        elif main_menu_choice == "9":
            print("Thank you for using this program. Goodbye.")
            sys.exit()
        else:
            print(
                "\033[31m" + "Error: Invalid input. Choose one of the displayed options.\n" + "\033[0m",
                file=sys.stderr
            )


def backup_menu():
    """Placeholder for backup menu."""
    print("")


def get_export_destination(item_name):
    """
    Helper function to help the folder selection and confirmation process.

    Args:
        item_name (str): The name of the item being exported (used for UI printing).

    Returns:
        str | None: The verified destination path, or None if the user cancels.
    """
    print(f"\nHow would you like to select the destination folder for {item_name}?")
    print("1. Select via GUI")
    print("2. Enter path manually")
    print("3. Cancel")

    dest_choice = input("\nChoose an option: ").strip()
    dest_path = None

    if dest_choice == "1":
        dest_path = gui_pick_folder()
        if not dest_path:
            print("Export cancelled.")
            return None
    elif dest_choice == "2":
        dest_path = input("Enter destination folder path: ").strip()
        if not dest_path:
            print("Export cancelled.")
            return None
    elif dest_choice == "3":
        print("Export cancelled.")
        return None
    else:
        print("Invalid choice. Export cancelled.")
        return None

    print(f"\nPreparing to export {item_name} to: {dest_path}")
    confirm = input("Proceed? (y/n): ")
    if confirm.lower() != "y":
        print("Export cancelled.")
        return None

    return dest_path


def export_all_menu():
    """
    Handles the UI flow for exporting all eligible albums.
    Applies current SettingsService filters automatically via the backend.
    """
    print("\n--- EXPORT ALL ---")
    if not backup_service.current_model:
        print(
            "[!] Error: No backup loaded. Please load a backup first.",
            file=sys.stderr,
        )
        return

    dest_path = get_export_destination("all albums")
    if not dest_path:
        return  # User cancelled somewhere in the helper loop

    # TODO:When export all function is implemented
    # success, message = export_service.export_all(backup_service.current_model, dest_path)


# if success:
#    print(f"\n[SUCCESS] {message}\n")
#  else:
#    print(f"\n[ERROR] {message}\n")


def export_specific_menu():
    """
    Handles the UI flow for exporting a single, user-selected album.
    Provides alphabetized options and input validation.
    """

    print("\n--- EXPORT SPECIFIC ALBUM ---")

    if not backup_service.current_model:
        print(
            "[!] Error: No backup loaded. Please load a backup first.",
            file=sys.stderr,
        )
        return

    available_albums = export_service.get_album_list(backup_service.current_model)

    if not available_albums:
        print(
            "[!] No albums found in backup.",
            file=sys.stderr,
        )
        return

    selected_album = None
    while True:
        print(f"\nFound {len(available_albums)} albums:")
        for album in available_albums:
            print(f" - {album}")

        choice = input(
            "\nEnter exact Album Name to export (or 'cancel' to go back): "
        ).strip()
        
        if choice.lower() == "cancel":
            print("Export cancelled.")
            return
        if choice in available_albums:
            selected_album = choice
            break
        else:
            print(
                f"\n[!] Error: Album '{choice}' does not exist.",
                file=sys.stderr,
            )

    dest_path = get_export_destination(f"'{selected_album}'")
    if not dest_path:
        return

    # TODO:When exporting a single album is implemented


# success, message = export_service.export_single_album(
#     backup_model=backup_service.current_model,
#   album_name=selected_album,
#      destination_str=dest_path
#  )

# if success:
#      print(f"\n[SUCCESS] {message}\n")
#  else:
#      print(f"\n[ERROR] {message}\n")


def settings_menu():
    """
    Displays and manages the Blacklist/Whitelist export filters.
    Disables access to modification submenus if a backup is not yet loaded.
    """

    while True:
        # Get data from Service
        mode, album_list = settings_service.get_state()

        backup_loaded = backup_service.current_model is not None

        print("\n--- SETTINGS ---")
        print(f"Mode: {mode}")
        print(f"List: [{album_list}]")

        if backup_loaded:
            print("1. Switch Mode (Whitelist/Blacklist)")
            print("2. Add/Remove Album")

        else:
            print("1. Switch mode (DISABLED - Load a backup first)")
            print("2. Add/Remove Album (DISABLED - Load a backup first)")
            print("3. Back")

        choice = input("Select: ")

        if choice == "1":
            if backup_loaded:
                print(settings_service.toggle_mode())
            else:
                print(
                    "\n[!] Error: You must load a backup before changing settings.",
                    file=sys.stderr,
                )
        elif choice == "2":
            if backup_loaded:
                album_selection_submenu()
            else:
                print("\n[!] Error: You must load a backup before selecting albums.")
        elif choice == "3":
            return
        else:
            print("\nInvalid Choice")


def album_selection_submenu():
    """
    Submenu to handle how users pick albums to filter.
    Includes a continuous entry loop for rapid manual list building.
    """
    available_albums = sorted(
        export_service.get_album_list(backup_service.current_model)
    )

    print("\n--- ALBUM SELECTION ---")
    print("Available Albums in Backup:")
    for album in available_albums:
        print(f" - {album}")

    print("\nHow would you like to select an album?")
    print("1. Manual Entry")
    print("2. Checkbox Style Menu")
    print("3. Go Back")

    sub_choice = input("\nSelect an option: ").strip()

    if sub_choice == "1":

        while True:
            _, current_list = settings_service.get_state()
            print(f"\nCurrent List: [{current_list}]")

            name = input("Enter exact Album Name (or type 'done' to finish): ").strip()

            # Exit condition
            if name.lower() == "done" or name == "":
                break

            # UI Validation
            if name in available_albums:
                success, msg = settings_service.toggle_album(name)
                print(msg)
            else:
                print(
                    f"\n[!] Error: Album '{name}' does not exist in the current backup.",
                    file=sys.stderr
                )

    elif sub_choice == "2":
        print("\n[!] Checkbox style menu coming soon!")

    elif sub_choice == "3":
        return

    else:
        print("\nInvalid choice.")

def help_user():
    """Links user to our documentations that explains how our program works."""
    dev_doc = "https://github.com/Gustakev/cs362-class-project/blob/main/documentation/iExtract-Developer-Documentation.md"
    user_doc = "https://github.com/Gustakev/cs362-class-project/blob/main/documentation/iExtract-User-Documentation.md"


    while True:
        print("1. User Documentation")
        print("2. Developer Documentation")
        print("3. Back\n")
        
        choice = int(input("Option: "))
        
        if choice == 1:
            webbrowser.open_new_tab(dev_doc)
        elif choice == 2:
            webbrowser.open_new_tab(user_doc)
        elif choice == 3:
            break
        else:
            print(
                "\033[31m" + "Error: Invalid input. Choose one of the displayed options.\n" + "\033[0m",
                file=sys.stderr,
            )

def report_bug():
    """Links to github issues if there is a bug found."""
    issues_url = "https://github.com/Gustakev/cs362-class-project/issues/new"
    print("Loading...")
    webbrowser.open_new_tab(issues_url)
    return

# TODO:
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

