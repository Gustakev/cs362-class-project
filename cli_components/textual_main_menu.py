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

from functional_components.services import BackupService, SettingsService, ExportService, ConversionService
from cli_components.main_menu import gui_pick_folder
#from functional_components.photo_captioner import get_caption




from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal, Center
from textual.widgets import Header, Footer, Button, Static, Input, Log, Label
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import ProgressBar
from textual import work




class iExtractApp(App):
    """The main TUI Application Class"""
# CSS Styling for the layout
   
    CSS_PATH = "main_menu.tcss"
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def __init__(self):
        super().__init__()
        # Initialize services here so 'self.settings_service' exists
        self.backup_service = BackupService()
        self.settings_service = SettingsService()
        self.export_service = ExportService()
        self.conversion_service = ConversionService()


    def compose(self) -> ComposeResult:
        """
        Main program command-line interface loop.
        """
       
        yield Header()
        yield Footer()

        #Main menu navigation
        with Vertical(id = "side_bar"):
            yield Label("[b]MAIN MENU[/b]", id="lbl_menu_title")
            with Vertical(id = "main_menu"):
                yield Button("1. Load iPhone Backup Folder", id = "btn_load")
                yield Button("2. Export All Camera Roll Media", id = "btn_export_all")
                yield Button("3. Export Specific Camera Roll Media", id = "btn_specific")
                yield Button("4. Settings", id= "btn_settings")
                yield Button("5. Help", id="btn_help")
                yield Button("6. Report Bug", id="btn_bug")
                yield Button("7. Photo Descriptor (Beta)", id="btn_photo_beta")
                yield Button("8. Exit", id="btn_exit", variant="error")
            #Load options
            with Vertical(id = "backup_options", classes="hidden"):
                yield ProgressBar(id="pb_loading", classes="hidden",show_percentage=True)
                yield Button("1. Load via GUI", id="btn_load_gui", variant="primary")
                yield Button("2. Load via Path", id="btn_load_path")
                yield Input(placeholder="Enter folder path...", id="input_path", classes="hidden")
                yield Button("Submit Path", id="btn_submit_path", classes="hidden", variant="success")
                yield Button("Go Back", id="btn_back_load")

            #Settings options     
            with Vertical(id="settings_options", classes="hidden"):
                yield Label("Mode: Unknown", id="lbl_settings_mode")
                yield Button("Toggle Whitelist/Blacklist", id="btn_toggle_mode")
                yield Button("Manage Album List", id="btn_manage_albums")
                yield Button("Go Back", id="btn_back_settings")

            # HELP OPTIONS
            with Vertical(id="help_options", classes="hidden"):
                yield Button("User Documentation", id="btn_help_user")
                yield Button("Developer Documentation", id="btn_help_dev")
                yield Button("Go Back", id="btn_back_help")

            #  EXPORT OPTIONS
            with Vertical(id="export_options", classes="hidden"):
                yield Label("Destination for: all albums", id="lbl_export_item")
                yield Button("1. Select via GUI", id="btn_export_gui", variant="primary")
                yield Button("2. Enter path manually", id="btn_export_path")
                yield Input(placeholder="Enter destination folder path...", id="input_export_path", classes="hidden")
                yield Button("Submit Path", id="btn_submit_export_path", classes="hidden", variant="success")
                
                # Confirmation step 
                yield Label("", id="lbl_export_confirm", classes="hidden")
                yield Button("Proceed (Yes)", id="btn_export_confirm_yes", classes="hidden", variant="success")
                yield Button("Cancel", id="btn_export_cancel", variant="error")


            # SPECIFIC EXPORT OPTIONS 
            with Vertical(id="specific_export_options", classes="hidden"):
                yield Label("Available Albums:", id="lbl_available_albums")
                yield Input(placeholder="Enter exact Album Name (or type 'cancel')...", id="input_specific_album")
                yield Button("Submit Album", id="btn_submit_specific_album", variant="success")
                yield Button("Go Back", id="btn_back_specific")   




        with Vertical (id = "main_content"):
            yield Label("System Log:")
            yield Log(id = "log_window",highlight= True)    

    def on_button_pressed(self, event: Button.Pressed) -> None:

        """Handles all button clicks"""
     
        log = self.query_one("#log_window",Log)

        btn_id = event.button.id

        if btn_id == "btn_exit":
            self.exit()

        """Navigation logic"""

        # Loading backup buttons
        if btn_id == "btn_load":
            self.query_one("#main_menu").add_class("hidden")
            self.query_one("#backup_options").remove_class("hidden")
            self.query_one("#lbl_menu_title").update("[b]LOAD BACKUP[/b]")
            log.write_line("[MENU] Select load method...")  

        # Returning from the backup loading menu to the main menu
        if btn_id == "btn_back_load":
            self.query_one("#backup_options").add_class("hidden")
            self.query_one("#main_menu").remove_class("hidden")
            self.query_one("#lbl_menu_title").update("[b]MAIN MENU[/b]")
            log.write_line("[MENU] Returned to Main Menu...") 
                  
        # Hiding main menu and showing settings options 
        if btn_id == "btn_settings_options":
            self.query_one("#main_menu").add_class("hidden")
            self.query_one("#settings_options").remove_class("hidden")
            self.query_one("#lbl_menu_title").update("[b]SETTINGS[/b]")
            # Update settings label from service
            mode, albums = self.settings_service.get_state()
            self.query_one("#lbl_settings_mode").update(f"Current Mode: {mode}") 

        # Returning from settings menu to main menu
        if btn_id == "btn_back_settings":
            self.query_one("#settings_options").add_class("hidden")
            self.query_one("#main_menu").remove_class("hidden")
            self.query_one("#lbl_menu_title").update("[b]MAIN MENU[/b]")
            log.write_line("[MENU] Returned to Main Menu...") 

        #Help menu
        if btn_id == "btn_help":
                self.query_one("#main_menu").add_class("hidden")
                self.query_one("#help_options").remove_class("hidden")
                self.query_one("#lbl_menu_title").update("[b]HELP & DOCS[/b]")

        if btn_id == "btn_back_help":
            self.query_one("#help_options").add_class("hidden")
            self.query_one("#main_menu").remove_class("hidden")
            self.query_one("#lbl_menu_title").update("[b]MAIN MENU[/b]")
            log.write_line("[MENU] Returned to Main Menu...") 


         # Route to the export options menu
        if btn_id == "btn_export_all":
            self.query_one("#main_menu").add_class("hidden")
            self.query_one("#export_options").remove_class("hidden")
            self.query_one("#lbl_menu_title").update("[b]EXPORT DESTINATION[/b]")
            self.query_one("#lbl_export_item").update("Destination for: all albums")
                
           
         

        """Action Logic"""

         # --- Getting Backup location logic -- 

        if btn_id == "btn_load_gui":
            selected_folder = gui_pick_folder()
            
            if selected_folder:
                log.write_line(f"\nYou chose: {selected_folder}")
                self.run_backup_load(selected_folder)

        # Logic for picking backup using a direct path
        if btn_id == "btn_load_path":
            self.query_one("#input_path").remove_class("hidden")
            self.query_one("#btn_submit_path").remove_class("hidden")
            
        if btn_id == "btn_submit_path":
            selected_folder = self.query_one("#input_path", Input).value
            if selected_folder:
                self.run_backup_load(selected_folder)

        
        #Export all logic 

        # --- EXPORT ALL ---
        if btn_id == "btn_export_all":
            if self.backup_service.current_model is None:
                log.write_line("[!] Error: No backup loaded. Please load a backup first.")
            else:
                self.current_export_target = "all albums" # Track the target
                log.write_line("\n--- EXPORT ALL ---")
                self.query_one("#main_menu").add_class("hidden")
                self.query_one("#export_options").remove_class("hidden")
                self.query_one("#lbl_menu_title").update("[b]EXPORT DESTINATION[/b]")
                self.query_one("#lbl_export_item").update("Destination for: all albums")
                
              

        # --- EXPORT DESTINATION HELPER LOGIC ---
        if btn_id == "btn_export_cancel":
            log.write_line("Export cancelled.")
            self.query_one("#export_options").add_class("hidden")
            self.query_one("#main_menu").remove_class("hidden")
            self.query_one("#lbl_menu_title").update("[b]MAIN MENU[/b]")

        if btn_id == "btn_export_gui":
            dest_path = gui_pick_folder()
            if not dest_path:
                log.write_line("Export cancelled.")
                self.query_one("#export_options").add_class("hidden")
                self.query_one("#main_menu").remove_class("hidden")
                self.query_one("#lbl_menu_title").update("[b]MAIN MENU[/b]")
            else:
                # Trigger the confirmation state
                self.query_one("#btn_export_gui").add_class("hidden")
                self.query_one("#btn_export_path").add_class("hidden")
                
                confirm_lbl = self.query_one("#lbl_export_confirm", Label)
                confirm_lbl.update(f"\nPreparing to export to: {dest_path}")
                confirm_lbl.remove_class("hidden")
                self.query_one("#btn_export_confirm_yes").remove_class("hidden")
                
                # Store the path temporarily so the confirm button knows where to export
                self.query_one("#btn_export_confirm_yes").tooltip = dest_path

        if btn_id == "btn_export_path":
            self.query_one("#input_export_path").remove_class("hidden")
            self.query_one("#btn_submit_export_path").remove_class("hidden")

        if btn_id == "btn_submit_export_path":
            dest_path = self.query_one("#input_export_path", Input).value
            if not dest_path:
                log.write_line("Export cancelled.")
                self.query_one("#export_options").add_class("hidden")
                self.query_one("#main_menu").remove_class("hidden")
                self.query_one("#lbl_menu_title").update("[b]MAIN MENU[/b]")
            else:
                # Trigger the confirmation state
                self.query_one("#btn_export_gui").add_class("hidden")
                self.query_one("#btn_export_path").add_class("hidden")
                self.query_one("#input_export_path").add_class("hidden")
                self.query_one("#btn_submit_export_path").add_class("hidden")

                confirm_lbl = self.query_one("#lbl_export_confirm", Label)
                confirm_lbl.update(f"\nPreparing to export to: {dest_path}")
                confirm_lbl.remove_class("hidden")
                self.query_one("#btn_export_confirm_yes").remove_class("hidden")
                
                self.query_one("#btn_export_confirm_yes").tooltip = dest_path

        if btn_id == "btn_export_confirm_yes":
            dest_path = self.query_one("#btn_export_confirm_yes").tooltip
            target = getattr(self, 'current_export_target', 'all albums')
            
            log.write_line(f"[INFO] Executing export for {target} to {dest_path}")
            
            # Execute the correct service method based on the tracked target
            if target == "all albums":
                success, message = self.export_service.export_all(
                    self.backup_service.current_model, 
                    dest_path, 
                    self.settings_service, 
                    self.conversion_service
                )
            else:
                success, message = self.export_service.export_single_album(
                    backup_model=self.backup_service.current_model,
                    destination_str=dest_path,
                    album_name=target,
                    settings_service=self.settings_service,
                    conversion_service=self.conversion_service
                )
            
            if success:
                log.write_line(f"\n[SUCCESS] {message}\n")
            else:
                log.write_line(f"\n[ERROR] {message}\n")
            
            # Return to main menu
            self.query_one("#export_options").add_class("hidden")
            self.query_one("#main_menu").remove_class("hidden")
            self.query_one("#lbl_menu_title").update("[b]MAIN MENU[/b]")



    # --- EXPORT SPECIFIC LOGIC ---
        if btn_id == "btn_specific":
            if not self.backup_service.current_model:
                log.write_line("[!] Error: No backup loaded. Please load a backup first.")
            else:
                available_albums = self.export_service.get_album_list(self.backup_service.current_model)
                if not available_albums:
                    log.write_line("[!] No albums found in backup.")
                else:
                    self.query_one("#main_menu").add_class("hidden")
                    self.query_one("#specific_export_options").remove_class("hidden")
                    self.query_one("#lbl_menu_title").update("[b]EXPORT SPECIFIC ALBUM[/b]")

                    # Display the list of albums 
                    album_text = f"Found {len(available_albums)} albums:\n" + "\n".join([f" - {a}" for a in available_albums])
                    self.query_one("#lbl_available_albums").update(album_text)

        if btn_id == "btn_back_specific":
            self.query_one("#specific_export_options").add_class("hidden")
            self.query_one("#main_menu").remove_class("hidden")
            self.query_one("#lbl_menu_title").update("[b]MAIN MENU[/b]")

        if btn_id == "btn_submit_specific_album":
            choice = self.query_one("#input_specific_album", Input).value.strip()
            available_albums = self.export_service.get_album_list(self.backup_service.current_model)

            if choice.lower() == "cancel":
                log.write_line("Export cancelled.")
                self.query_one("#input_specific_album", Input).value = ""
                self.query_one("#specific_export_options").add_class("hidden")
                self.query_one("#main_menu").remove_class("hidden")
                self.query_one("#lbl_menu_title").update("[b]MAIN MENU[/b]")
                return

            # Strict 1:1 check as written in the CLI
            if choice in available_albums:
                self.query_one("#input_specific_album", Input).value = "" # Clear input
                self.current_export_target = choice # Track target for execution step
                
                # Hand off to the destination path picker (get_export_destination equivalent)
                self.query_one("#specific_export_options").add_class("hidden")
                self.query_one("#export_options").remove_class("hidden")
                self.query_one("#lbl_menu_title").update("[b]EXPORT DESTINATION[/b]")
                self.query_one("#lbl_export_item").update(f"Destination for: '{choice}'")
            else:
                log.write_line(f"[!] Error: Album '{choice}' does not exist.")



    @work(thread=True)
    def run_backup_load(self, selected_folder):
        """Background worker for backup loading."""
        log = self.query_one("#log_window")
        pb = self.query_one("#pb_loading")
        options_menu = self.query_one("#backup_options")
        
        # Show  progress bar
        pb.remove_class("hidden")
        options_menu.disabled = True 
        log.write_line("[LOADING] Parsing backup database...")

        #  Call the service 
        success, message = self.backup_service.attempt_load_backup(selected_folder)
        
        options_menu.disabled = False
        pb.add_class("hidden")
        if success:
            log.write_line(f"[SUCCESS] {message}")
            log.write_line(self.backup_service.get_formatted_device_metadata())
            self.query_one("#backup_options").add_class("hidden")
            self.query_one("#main_menu").remove_class("hidden")
        else:
            log.write_line(f"[ERROR] {message}")


def main():
    """
    Program entrypoint.
    """
    app = iExtractApp()
    app.run()

if __name__ == "__main__":
    main()
