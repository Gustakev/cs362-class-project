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
from cli_components.main_menu import gui_pick_folder
#from functional_components.photo_captioner import get_caption

backup_service = BackupService()
settings_service = SettingsService()
export_service = ExportService()



from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal, Center
from textual.widgets import Header, Footer, Button, Static, Input, Log, Label
from textual.reactive import reactive
from textual.screen import Screen




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

        # Logic for picking backup location using folder gui

        if btn_id == "btn_load_gui":
            selected_folder = gui_pick_folder()
            
            if selected_folder:
                log.write_line(f"\nYou chose: {selected_folder}")
                
            
                success, message = backup_service.attempt_load_backup(selected_folder)
                
                if success:
                    log.write_line(f"\n{message}")
                    log.write_line(backup_service.get_formatted_device_metadata())
                    log.write_line("")
                    
                    # Returning to the main menu
                    self.query_one("#backup_options").add_class("hidden")
                    self.query_one("#main_menu").remove_class("hidden")
                    self.query_one("#lbl_menu_title").update("[b]MAIN MENU[/b]")
                else:
                    #  staying on the menu
                    log.write_line(f"\n[ERROR]{message}\n")

        # Logic for picking backup using a direct path
        if btn_id == "btn_load_path":
            self.query_one("#input_path").remove_class("hidden")
            self.query_one("#btn_submit_path").remove_class("hidden")
            
        if btn_id == "btn_submit_path":
            selected_folder = self.query_one("#input_path", Input).value
            
            if selected_folder:
                log.write_line(f"\nYou chose: {selected_folder}")
                
                
                success, message = backup_service.attempt_load_backup(selected_folder)
                
                if success:
                    log.write_line(f"\n{message}")
                    log.write_line(backup_service.get_formatted_device_metadata())
                    log.write_line("")
                    
                    # Clean up the input box
                    self.query_one("#input_path", Input).value = ""
                    
                    #  the user back to the Main Menu
                    self.query_one("#backup_options").add_class("hidden")
                    self.query_one("#main_menu").remove_class("hidden")
                    self.query_one("#lbl_menu_title").update("[b]MAIN MENU[/b]")
                else:
                    log.write_line(f"\n[ERROR]{message}\n")

        
        #Export all logic 

        # --- EXPORT ALL ---
        if btn_id == "btn_export_all":
            if backup_service.current_model is None:
                log.write_line("[!] Error: No backup loaded. Please load a backup first.")
            else:
                log.write_line("\n--- EXPORT ALL ---")
                
              

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
            # Retrieve the path we stored during the selection step
            dest_path = self.query_one("#btn_export_confirm_yes").tooltip
            item_name = str(self.query_one("#lbl_export_item", Label).renderable)
            
            # Execute the export
            log.write_line(f"[INFO] Executing export for {item_name} to {dest_path}")
            
            # TODO: When export all function is implemented
            # success, message = export_service.export_all(backup_service.current_model, dest_path)
            # if success:
            #     log.write_line(f"\n[SUCCESS] {message}\n")
            # else:
            #     log.write_line(f"\n[ERROR] {message}\n")
            
            # Return to main menu
            self.query_one("#export_options").add_class("hidden")
            self.query_one("#main_menu").remove_class("hidden")
            self.query_one("#lbl_menu_title").update("[b]MAIN MENU[/b]")

def main():
    """
    Program entrypoint.
    """
    app = iExtractApp()
    app.run()

if __name__ == "__main__":
    main()
