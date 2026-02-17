"""
Author: Kevin Gustafson
Date: 2026-01-29
Program Description: Command line interface for iExtract.
"""

import sys

import tkinter as tk
from tkinter import filedialog

from pathlib import Path

from functional_components.backup_locator_and_validator.app. \
    backup_model_builder import build_backup_model


from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Header, Footer, Button, Static, Input, Log, Label
from textual.reactive import reactive


"""Global variables and constants."""
BACKUP_MODEL = None


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
    global BACKUP_MODEL

    print(f"Device Name: {BACKUP_MODEL.backup_metadata.source_device.name}")

    # Reformat the device model so it looks better:
    formatted_model = (BACKUP_MODEL.backup_metadata.source_device.model). \
        split(",")[0]
    formatted_model = formatted_model.replace("e", "e ")

    submodel = (BACKUP_MODEL.backup_metadata.source_device.model).split(",")[1]

    print(f"Device Model: {formatted_model}")
    print(f"Device Submodel: {submodel}")
    print(f"Device Version: {BACKUP_MODEL.backup_metadata. \
        source_device.ios_version}")


def load_backup_menu():
    """
    Submenu for choosing how to pick the backup folder.
    """
    global BACKUP_MODEL # The persistent backup model.

    while True:
        print(
            "*** Instructions: Enter a number corresponding to the choices "
            "below. ***\n"
        )
        print("1. Load iPhone Backup Folder Via GUI")
        print("2. Load iPhone Backup Folder By Entering File Path")
        print("3. Go Back")

        folder_picker_method = input("\nChoose an option: ")
        print("")

        if folder_picker_method == "1":
            selected_folder = gui_pick_folder()
            
            # Displays folder picking error if user cancels or it is not
            # available.
            if selected_folder is None:
                # GUI unavailable.
                print("This system does not support GUI folder selection.\n")
                continue
            
            if selected_folder == "":
                # User canceled folder selection dialog.
                print("User canceled selection. No folder selected. Please " \
                      "try again.\n")
                continue
            
            print("You chose:", selected_folder)
            print("\n")
            # TODO: Attempt to load the backup. If loading fails, print an
            # error and continue the loop to let the user choose again.

            # Attempt loading backup.
            result = build_backup_model(Path(selected_folder))

            # If BackupModel was not successfully made:
            if result.success != True:
                print("Error loading backup:")
                print(result.error)
                print("")

                # Try again.
                continue
            
            # If the BackupModel was successfully made:
            BACKUP_MODEL = result.backup_model
            print("Backup loaded successfully!")
            print_device_metadata()
            print("")
            return

        elif folder_picker_method == "2":
            selected_folder = input("Enter the path to your iPhone backup " \
                "folder: ")
            print("")
            print("You chose:", selected_folder)
            print("\n")
            # TODO: Attempt to load the backup. If loading fails, print an
            # error and continue the loop to let the user choose again.

            # Attempt loading backup.
            result = build_backup_model(Path(selected_folder))

            # If BackupModel was not successfully made:
            if result.success != True:
                print("Error loading backup:")
                print(result.error)
                print("")
                
                # Try again.
                continue
            
            # If the BackupModel was successfully made:
            BACKUP_MODEL = result.backup_model
            print("Backup loaded successfully!")
            print_device_metadata()
            print("")
            return

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
            "\n========================= iExtract Main Menu ============="
            "============"
        )
        print(
            "\n*** Instructions: Enter a number corresponding to the "
            "choices below. ***\n"
        )
        print("1. Load iPhone Backup Folder")
        print("2. Export All Camera Roll Media")
        print("3. Export Specific Camera Roll Media")
        print("4. Settings")
        print("5. Exit")

class iExtractApp(App):
    """The main TUI Application Class"""
# CSS Styling for the layout
   
    CSS_PATH = "main_menu.tcss"
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        """
        Main program command-line interface loop.
        """
       

        yield Header()
        yield Footer()


        with Vertical(id = "side_bar"):
            yield Label("[b]MAIN MENU[/b]", id="lbl_menu_title")
            with Vertical(id = "main_menu"):
                yield Button("1. Load iPhone Backup Folder", id = "btn_load")
                yield Button("2. Export All Camera Roll Media", id = "btn_export")
                yield Button("3. Export Specific Camera Roll Media", id = "btn_specific")
                yield Button("4. Settings", id= "btn_settings")
                yield Button("5. Exit", id = "btn_exit")

            with Vertical(id = "backup_options", classes="hidden"):
                yield Button("1. Load via GUI", id="btn_load_gui", variant="primary")
                yield Button("2. Load via Path", id="btn_load_path")
                yield Button("3. Go Back", id="btn_back")

        with Vertical (id = "main_content"):
            yield Label("System Log:")
            yield Log(id = "log_window",highlight= True)


    def on_button_pressed(self, event: Button.Pressed) -> None:

        """Handles all button clicks"""
        global BACKUP_MODEL
        log = self.query_one("#log_window",Log)

        btn_id = event.button.id

        if btn_id == "btn_exit":
            self.exit()

        """Navigation logic"""

        if btn_id == "btn_load":
            self.query_one("#main_menu").add_class("hidden")
            self.query_one("#backup_options").remove_class("hidden")
            self.query_one("#lbl_menu_title").update("[b]LOAD BACKUP[/b]")
            log.write_line("[MENU] Select load method...")  


        if btn_id == "btn_back":
            self.query_one("#backup_options").add_class("hidden")
            self.query_one("#main_menu").remove_class("hidden")
            self.query_one("#lbl_menu_title").update("[b]MAIN MENU[/b]")
            log.write_line("[MENU] Returned to Main Menu...") 
                  

        """Action Logic"""

        if btn_id == "btn_load_gui":
            log.write_line("[INFO] Opening GUI folder picker...")
            folder = gui_pick_folder()
            if folder:
                log.write_line(f"[INFO] Selected folder: {folder}")
                
            else:
                log.write_line("[WARN] Selection caccelled...")
        


    def action_toggle_dark(self)-> None:
        self.theme = ("textual-dark" if self.theme == "textual-light" else "textual-light") 


        


        
    

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
    app = iExtractApp()
    app.run()


if __name__ == "__main__":
    app = iExtractApp()
    app.run()
