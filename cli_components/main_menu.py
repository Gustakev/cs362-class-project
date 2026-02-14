"""
Author: Kevin Gustafson
Date: 2026-01-29
Program Description: Command line interface for iExtract.
"""

import sys
import tkinter as tk
from tkinter import filedialog


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


def load_backup_menu():
    """
    Submenu for choosing how to pick the backup folder.
    """
    while True:
        print(
            "*** Instructions: Enter the number corresponding to the choices "
            "below. ***\n"
        )
        print("1. Load iPhone Backup Folder Via GUI")
        print("2. Load iPhone Backup Folder By Entering File Path")
        print("3. Go Back")

        folder_picker_method = input("\nChoose an option: ")
        print("")

        if folder_picker_method == "1":
            selected_folder = gui_pick_folder()
            if not selected_folder:
                print("This system does not support GUI folder selection.\n")
                continue

            print("You chose:", selected_folder)
            print("\n")
            # TODO: Attempt to load the backup. If loading fails, print an
            # error and continue the loop to let the user choose again.
            return

        elif folder_picker_method == "2":
            selected_folder = input(
                "Enter the path to your iPhone backup "
                "folder: "
            )
            print("")
            print("You chose:", selected_folder)
            print("\n")
            # TODO: Attempt to load the backup. If loading fails, print an
            # error and continue the loop to let the user choose again.

        elif folder_picker_method == "3":
            print("\nGoing back...\n")
            return

        else:
            print(
                "Error: Invalid input. Choose one of the displayed options.",
                file=sys.stderr
            )
            print("")


def main_menu():
    """
    Main program command-line interface loop.
    """
    while True:
        print(
            "\n=========================== iExtract Main Menu ============="
            "=============="
        )
        print(
            "\n*** Instructions: Enter the number corresponding to the "
            "choices below. ***\n"
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
            print("Export All Camera Roll Media (not implemented yet)\n")
        elif main_menu_choice == "3":
            print("Export Specific Camera Roll Media (not implemented yet)\n")
        elif main_menu_choice == "4":
            print("Settings (not implemented yet)\n")
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
    """Placeholder for export-all menu."""
    print("")


def export_specific_menu():
    """Placeholder for export-specific menu."""
    print("")


def settings_menu():
    """Placeholder for settings menu."""
    print("")


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
