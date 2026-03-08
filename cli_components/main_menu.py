"""
Author: Kevin Gustafson (Brendon Wong worked on 2026-02-26)
Date: 2026-01-29
Program Description: Command line interface for iExtract.
"""

import sys
import os

import tkinter as tk
from tkinter import filedialog

import webbrowser

from pathlib import Path
from PIL import Image

from functional_components.services import BackupService, SettingsService, \
    ExportService, ConversionService
from functional_components.photo_caption.app import photo_captioner

backup_service = BackupService()
settings_service = SettingsService()
export_service = ExportService()
conversion_service = ConversionService()

def restart_program():
    """
    Resets global state to mimic a fresh application start.

    """
    global backup_service, settings_service, export_service, conversion_service

    backup_service = BackupService()
    settings_service = SettingsService()
    export_service = ExportService()
    conversion_service = ConversionService()
    print("\nApplication state has been reset. Restarting...\n")


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

        print("Window opened. Please select a folder.")
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
        print(f"\033[33m" + "** Instructions: Enter a number corresponding to the choices below. **\n"+ "\033[0m")
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
            selected_folder = input(r"Enter the path to your iPhone backup folder (e.g 'C:\Users\[Username]\Apple\MobileSync\Backup' or '~/Library/Application Support/MobileSync/Backup/'): ")
            print("")
            print("You chose:", selected_folder)
        elif folder_picker_method == "3":
            print("\nGoing back...\n")
            return
        else:
            print(
                "\033[31m" + "\nError: Invalid input. Choose one of the displayed options." + "\033[0m",
                file=sys.stderr,
            )
            print("")
            continue

        success, message, warning = backup_service.attempt_load_backup(selected_folder)

        if success:
            print(f"\n{message}")
            print(backup_service.get_formatted_device_metadata())
            if warning:
                print(
                    "\033[31m" + f"\n{warning}" + "\033[0m",
                    file=sys.stderr
                )
            print("")
            return
        else:
            print(f"\n{message}\n")

def main_menu():
    """
    Main program command-line interface loop.
    """
    while True:
        print("\033[33m" + "=========================== iExtract Menu ============================\n")
        print(f"** Instructions: Enter a number corresponding to the choices below. **\n"+ "\033[0m")

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
            feat_photo_caption()
        elif main_menu_choice == "8":
            restart_program()
            return
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
    while True:
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
            break
        elif dest_choice == "2":
            dest_path = input("Enter destination folder path: ").strip()
            if not dest_path:
                print("Export cancelled.")
                return None
            break
        elif dest_choice == "3":
            print("Export cancelled.")
            return None
        else:
            print("Invalid choice. Export cancelled.")
            
    while True:
        print(f"\nPreparing to export {item_name} to: {dest_path}")
        confirm = input("Proceed? (y/n): ").strip().lower()
        if confirm == 'y':
            return dest_path
        elif confirm == 'n':
            print("Export cancelled.")
            return None
        else:
            print("\033[31mInvalid input. Please enter 'y' or 'n'.\033[0m")

def export_all_menu():
    """
    Handles the UI flow for exporting all eligible albums.
    Applies current SettingsService filters automatically via the backend.
    """

    # Prevent exporting without a loaded backup
    if backup_service.current_model is None:
        print("\033[31m" + "[!] Error: No backup loaded. Please load a backup first." "\033[31m")
        return
    
    print("\n--- EXPORT ALL ---")

    dest_path = get_export_destination("all albums")
    if not dest_path:
        return  # User cancelled somewhere in the helper loop

    # Attempt extraction.
    success, message = export_service.export_all(
        backup_service.current_model,
        dest_path,
        settings_service,
        conversion_service
    )
    if success:
        print(f"\n[SUCCESS] {message}\n")
    else:
        print(f"\033[31m" + "\n[ERROR] {message}\n"+ "\033[0m" , file=sys.stderr)

def export_specific_menu():
    """
    Handles the UI flow for exporting a single, user-selected album.
    Provides alphabetized options and input validation.
    """

    print("\033[33m" + "\n--- EXPORT SPECIFIC ALBUM ---" + "\033[0m")

    if not backup_service.current_model:
        print(
            "\033[31m" + "[!] Error: No backup loaded. Please load a backup first." + "\033[0m",
            file=sys.stderr,
        )
        return

    available_albums = export_service.get_album_list(backup_service.current_model)

    if not available_albums:
        print(
            "\033[31m" + "[!] No albums found in backup." + "\033[0m",
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
                f"\033[31m" + "\n[!] Error: Album '{choice}' does not exist." + "\033[0m",
                file=sys.stderr,
            )
    
    # Do export of single collection:
    dest_path = get_export_destination(f"'{selected_album}'")
    if not dest_path:
        return

    success, message = export_service.export_single_album(
        backup_model=backup_service.current_model,
        destination_str=dest_path,
        album_name=selected_album,
        settings_service=settings_service,
        conversion_service=conversion_service
    )
    if success:
        print(f"\n[SUCCESS] {message}\n")
    else:
        print(f"\033[31m" + "\n[ERROR] {message}\n" + "\033[0m", file=sys.stderr)

def settings_menu():
    """Top-level settings menu. Routes to submenus."""
    if backup_service.current_model is None:
        print("\033[31m" + "\n[!] Error: You must load a backup before changing settings." + "\033[0m")
        return

    while True:
        print("\033[33m" + "\n--- SETTINGS ---" + "\033[0m")
        print("1. Blacklist/Whitelist Settings")
        print("2. Conversion Settings")
        print("3. Symlink Settings")
        print("4. Hidden Album Settings")
        print("5. Back")

        choice = input("Select: ").strip()

        if choice == "1":
            blacklist_whitelist_menu()
        elif choice == "2":
            conversion_settings_menu()
        elif choice == "3":
            symlink_settings_menu()
        elif choice == "4":
            hidden_album_settings_menu()
        elif choice == "5":
            print("Going back...")
            return
        else:
            print("\nInvalid Choice")

def blacklist_whitelist_menu():
    """Manages the Blacklist/Whitelist export filters."""
    while True:
        mode, album_list = settings_service.get_state()
        backup_loaded = backup_service.current_model is not None

        print("\033[33m" + "\n--- BLACKLIST/WHITELIST SETTINGS ---" + "\033[0m")
        print(f"Mode: {mode}")
        print(f"List: [{album_list}]")

        if backup_loaded:
            print("1. Switch Mode (Blacklist/Whitelist)")
            print("2. Add/Remove Album")
            print("3. Back")
        else:
            print("1. Switch mode (DISABLED - Load a backup first)")
            print("2. Add/Remove Album (DISABLED - Load a backup first)")
            print("3. Back")

        choice = input("Select: ")

        if choice == "1":
            if backup_loaded:
                available_albums = export_service.get_album_list(backup_service.current_model)
                print(settings_service.toggle_mode(available_albums))
            else:
                print("\033[31m" + "\n[!] Error: You must load a backup before changing settings." + "\033[0m", file=sys.stderr)
        elif choice == "2":
            if backup_loaded:
                album_selection_submenu()
            else:
                print("\033[31m" + "\n[!] Error: You must load a backup before selecting albums." + "\033[0m")
        elif choice == "3":
            return
        else:
            print("\nInvalid Choice")

def conversion_settings_menu():
    """Manages conversion format settings."""
    while True:
        print("\033[33m" + "\n--- CONVERSION SETTINGS ---" + "\033[0m")
        print("Toggle a conversion to enable/disable it. Enabled conversions")
        print("will automatically convert files during export.\n")

        conversions = ConversionService.SUPPORTED_CONVERSIONS
        for i, (src, dst) in enumerate(conversions.items(), start=1):
            status = "ON" if src in conversion_service.enabled else "OFF"
            print(f"{i}. {src} → {dst}  [{status}]")

        back_num = len(conversions) + 1
        print(f"{back_num}. Back")

        choice = input("\nSelect: ").strip()

        if choice == str(back_num):
            return
        
        try:
            idx = int(choice) - 1
            ext = list(conversions.keys())[idx]
            print(conversion_service.toggle(ext))
        except (ValueError, IndexError):
            print("\nInvalid Choice")


def symlink_settings_menu():
    """Manages symlink creation settings."""
    while True:
        print("\033[33m" + "\n--- SYMLINK SETTINGS ---" + "\033[0m")

        print(
            "- Enabling symlinks (symbolic links, or shortcuts) allows\n"
            "iExtract to save a file to the extraction folder one time and\n"
            "link to its location in every folder for each collection to\n"
            "which it belongs. This saves storage space on your system.\n"
            "- IMPORTANT WARNING: Ensure that the location you store your\n"
            "extraction in is the permanent location you would like to store\n"
            "it in. If you move the extraction folder (or rename it), you\n"
            "will have to run a script to change the path of each symlink to\n"
            "reflect the new, proper paths of each file in the extraction\n"
            "folder.\n"
            )

        status = "ON" if settings_service.use_symlinks else "OFF"
        print(f"Current Status: [{status}]")
        print("1. Toggle Symlinks")
        print("2. Back")

        choice = input("\nSelect: ").strip()

        if choice == "1":
            print("\n" + settings_service.toggle_symlinks())
        elif choice == "2":
            return
        else:
            print("\nInvalid Choice")
                

def hidden_album_settings_menu():
    """Manages hidden album exclusion settings."""
    while True:
        print("\033[33m" + "\n--- HIDDEN ALBUM SETTINGS ---" + "\033[0m")

        print(
            "- Enabling hidden album exclusion prevents the export of any\n"
            "media included in the hidden album.\n"
            )

        status = "ON" if settings_service.exclude_hidden_album else "OFF"
        print(f"Current Status: [{status}]")
        print("1. Toggle Hidden Album Exclusion")
        print("2. Back")

        choice = input("\nSelect: ").strip()

        if choice == "1":
            print("\n" + settings_service.toggle_exclude_hidden_album())
        elif choice == "2":
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

    print("\033[33m" + "\n--- ALBUM SELECTION ---" + "\033[0m")
    print("Available Albums in Backup:")

    for album in available_albums:
        print(f" - {album}")
    while True:
        print("\nHow would you like to select an album?")
        print("1. Manual Entry")
        print("2. Checkbox Style Menu")
        print("3. Go Back")

        sub_choice = input("\nSelect an option: ").strip()

        if sub_choice == "1":
            while True:
                _, current_list = settings_service.get_state()
                print(f"\nCurrent List: [{current_list}]")

                name = input("Enter exact Album Name (or type 'cancel' to finish): ").strip()

                # Exit condition
                if name.lower() == "cancel":
                    break

                # UI Validation
                if name in available_albums:
                    success, msg = settings_service.toggle_album(name)
                    print(msg)
                else:
                    print(
                        f"\033[31m" + f"\n[!] Error: Album '{name}' does not exist in the current backup." + "\033[0m",
                        file=sys.stderr
                    )
        elif sub_choice == "2":
            print("\n[!] Checkbox style menu coming soon!")
        elif sub_choice == "3":
            return
        else:
            print("\nInvalid choice.")

def help_user():
    """Links user to our documentation that explains how our program works."""
    dev_doc = "https://github.com/Gustakev/cs362-class-project/blob/main/documentation/iExtract-Developer-Documentation.md"
    user_doc = "https://github.com/Gustakev/cs362-class-project/blob/main/documentation/iExtract-User-Documentation.md"

    while True:
        print("\033[33m" + "========================= Documentation =========================\n" + "\033[0m")
        print("1. User Documentation")
        print("2. Developer Documentation")
        print("3. Back\n")

        choice = input("Option: ").strip()

        if choice == "1":
            webbrowser.open_new_tab(user_doc)
        elif choice == "2":
            webbrowser.open_new_tab(dev_doc)
        elif choice == "3":
            break
        else:
            print(
                "\033[31m" + "Error: Invalid input. Choose one of the displayed options.\n" + "\033[0m",
                file=sys.stderr
            )

def report_bug():
    """Links to github issues if there is a bug found."""
    issues_url = "https://github.com/Gustakev/cs362-class-project/issues/new"
    print("Loading...")
    webbrowser.open_new_tab(issues_url)
    return

def feat_photo_caption():
    """"""
    if getattr(sys, 'frozen', False):
        base = Path(sys._MEIPASS)
    else:
        base = Path(".")
    file_dir = base / "functional_components/photo_caption/data"
    root_dir = file_dir

    print("\033[33m" + "=========================== iExtract Menu ===========================\n")
    print(f"** Instructions: Enter a number corresponding to the choices below. **\n"+ "\033[0m")
    
    while True:

        folders = [p for p in file_dir.iterdir() if p.is_dir()]
        files = [p for p in file_dir.iterdir() if p.is_file()]
        entries = folders + files

        for i, p in enumerate(entries, start=1):
            print(f"{i}. {p.name}")

        back_option = len(entries) + 1
        print(f"{back_option}. Back\n")

        try:
            choice = int(input("Choice: "))
        except ValueError:
            print("\033[31mInvalid input. Enter a number.\033[0m\n")
            continue

        if choice == back_option:
            if file_dir == root_dir:
                break
            file_dir = file_dir.parent
            continue

        if not (1 <= choice <= len(entries)):
            print("\033[31m" + "Error: Choose one of the displayed options." + "\033[0m\n")
            continue

        selected = entries[choice - 1]

        if selected.is_dir():
            file_dir = selected
            continue

        ext = selected.suffix.lower()
        if ext in {".jpg", ".jpeg", ".png"}:
            caption = photo_captioner.get_caption(str(selected))
            image = Image.open(Path(selected))
            image.show()
            print("Loading...")
            print(f"\nCaption: {caption}\n")
        else:
            print("Unsupported file type. Please report bug.")


# TODO:
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
