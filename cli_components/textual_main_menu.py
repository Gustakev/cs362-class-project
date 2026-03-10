"""
Author: Noah Gregie
Date: 2026-01-29
Program Description: Textual GUI interface for iExtract.
"""

import sys

import tkinter as tk
from tkinter import filedialog

import webbrowser

from pathlib import Path

from functional_components.services import (
    BackupService,
    SettingsService,
    ExportService,
    ConversionService,
    draw_progress_bar,
)
from cli_components.main_menu import gui_pick_folder

from functional_components.photo_caption.app import photo_captioner
from PIL import Image

# from functional_components.photo_captioner import get_caption


from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal, Center
from textual.widgets import Header, Footer, Button, Static, Input, Log, Label
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import ProgressBar
from textual import work
from textual import on, work
from textual.widgets import DirectoryTree


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
        Constructs the UI layout.
        Hidden classes are used to store submenus that will be toggled on/off
        during user navigation.
        """

        yield Header()
        yield Footer()
        # Main wrapper dividing between menu and log output
        with Horizontal(id="app_grid"):

            # LEFT SIDEBAR: Interactive Menus

            with Vertical(id="side_bar"):
                yield Label("[b]MAIN MENU[/b]", id="lbl_menu_title")
                # --- 1. Main Menu Options ---
                with Vertical(id="main_menu"):
                    yield Button("1. Load iPhone Backup Folder", id="btn_load")
                    yield Button("2. Export All Camera Roll Media", id="btn_export_all")
                    yield Button(
                        "3. Export Specific Camera Roll Media", id="btn_specific"
                    )
                    yield Button("4. Settings", id="btn_settings")
                    yield Button("5. Help", id="btn_help")
                    yield Button("6. Report Bug", id="btn_bug")
                    yield Button("7. Photo Descriptor (Beta)", id="btn_photo_beta")
                    yield Button("8. Restart", id="btn_restart")
                    yield Button("9. Exit", id="btn_exit")
                # --- 2. Load Backup Submenu ---
                with Vertical(id="backup_options", classes="hidden"):
                    yield ProgressBar(id="pb_loading", classes="hidden")
                    yield Button(
                        "1. Load via GUI", id="btn_load_gui", variant="primary"
                    )
                    yield Button("2. Load via Path", id="btn_load_path")
                    yield Input(
                        placeholder="Enter folder path...",
                        id="input_path",
                        classes="hidden",
                    )
                    yield Button(
                        "Submit Path",
                        id="btn_submit_path",
                        classes="hidden",
                        variant="success",
                    )
                    yield Button("Go Back", id="btn_back_load")

                # --- 4. Main Settings Submenu ---
                with Vertical(id="settings_options", classes="hidden"):
                    yield Button("1. Blacklist/Whitelist Settings", id="btn_menu_bw")
                    yield Button("2. Conversion Settings", id="btn_menu_conv")
                    yield Button("3. Symlink Settings", id="btn_menu_symlink")
                    yield Button("4. Smart Album Settings", id="btn_menu_smart_album")
                    yield Button("5. Go Back", id="btn_back_settings")

                # --- 5. BLACKLIST / WHITELIST MENU ---
                with Vertical(id="bw_options", classes="hidden"):
                    yield Label("Mode: Unknown", id="lbl_bw_mode")
                    yield Label("List: []", id="lbl_bw_list")
                    yield Button("1. Switch Mode", id="btn_bw_switch")
                    yield Button("2. Add/Remove Album", id="btn_bw_manage")
                    yield Button("3. Go Back", id="btn_back_bw")

                # --- 6. ALBUM SELECTION (MANUAL ENTRY) ---
                with Vertical(id="album_selection_options", classes="hidden"):
                    yield Label("Available Albums:\n", id="lbl_album_avail")
                    yield Label("Current List: []", id="lbl_album_current")
                    yield Input(
                        placeholder="Enter exact Album Name ", id="input_manage_album"
                    )
                    yield Button(
                        "Submit Album", id="btn_submit_managed_album", variant="success"
                    )
                    yield Button("Go Back", id="btn_back_album_manage")

                # --- 7. CONVERSION SETTINGS ---
                with Vertical(id="conversion_options", classes="hidden"):
                    yield Label(
                        "Toggle a conversion to enable/disable it. Enabled conversions\nwill automatically convert files during export.\n"
                    )
                    yield Button("1. HEIC → JPG  [OFF]", id="btn_toggle_heic")
                    yield Button("2. MOV → MP4  [OFF]", id="btn_toggle_mov")
                    yield Button("3. Go Back", id="btn_back_conv")

                # --- 8. SYMLINK SETTINGS ---
                with Vertical(id="symlink_options", classes="hidden"):
                    yield Label(
                        "- Enabling symlinks (symbolic links, or shortcuts) allows\niExtract to save a file to the extraction folder one time and\nlink to its location... This saves storage space.\n"
                    )
                    yield Label("Current Status: [Unknown]", id="lbl_symlink_status")
                    yield Button("1. Toggle Symlinks", id="btn_toggle_symlink")
                    yield Button("2. Go Back", id="btn_back_symlink")

                # HELP OPTIONS
                with Vertical(id="help_options", classes="hidden"):
                    yield Button("User Documentation", id="btn_help_user")
                    yield Button("Developer Documentation", id="btn_help_dev")
                    yield Button("Go Back", id="btn_back_help")

                #  EXPORT DESTINATION PICKER
                with Vertical(id="export_options", classes="hidden"):
                    yield Label("Destination for: all albums", id="lbl_export_item")
                    yield Button(
                        "1. Select via GUI", id="btn_export_gui", variant="primary"
                    )
                    yield Button("2. Enter path manually", id="btn_export_path")
                    yield Input(
                        placeholder="Enter destination folder path...",
                        id="input_export_path",
                        classes="hidden",
                    )
                    yield Button(
                        "Submit Path",
                        id="btn_submit_export_path",
                        classes="hidden",
                        variant="success",
                    )
                    yield ProgressBar(
                        id="pb_export",
                        classes="hidden",
                        show_percentage=True,
                        show_eta=True,
                    )
                    # Confirmation step
                    yield Label("", id="lbl_export_confirm", classes="hidden")
                    yield Button(
                        "Proceed (Yes)",
                        id="btn_export_confirm_yes",
                        classes="hidden",
                        variant="success",
                    )
                    yield Button("Cancel", id="btn_export_cancel", variant="error")

                # SPECIFIC EXPORT OPTIONS
                with Vertical(id="specific_export_options", classes="hidden"):
                    yield Label("Available Albums:", id="lbl_available_albums")
                    yield Input(
                        placeholder="Enter exact Album Name (or type 'cancel')...",
                        id="input_specific_album",
                    )
                    yield Button(
                        "Submit Album",
                        id="btn_submit_specific_album",
                        variant="success",
                    )
                    yield Button("Go Back", id="btn_back_specific")

                # --- PHOTO DESCRIPTOR (BETA) ---
                with Vertical(id="photo_beta_options", classes="hidden"):
                    yield Label(
                        "Select an image (.jpg, .png) to generate a caption:",
                        id="lbl_photo_instructions",
                    )
                    yield DirectoryTree(
                        "functional_components/photo_caption/data/", id="photo_tree"
                    )
                    yield Label("", id="lbl_photo_caption")
                    yield Button("Go Back", id="btn_back_photo")

                # ---  SMART ALBUM SETTINGS ---
                with Vertical(id="smart_album_options", classes="hidden"):
                    yield Label(
                        "- Exclude specific smart albums from exports. When a smart album\nis excluded, media in that album is not exported, even if the\nalbum is whitelisted."
                    )
                    yield Label("Hidden Album: [Unknown]", id="lbl_hidden_status")
                    yield Label("Recently Deleted: [Unknown]", id="lbl_recently_deleted_status")
                    yield Button("1. Toggle Hidden Album", id="btn_toggle_hidden")
                    yield Button("2. Toggle Recently Deleted", id="btn_toggle_recently_deleted")
                    yield Button("3. Go Back", id="btn_back_smart_album")

            # RIGHT SIDEBAR: System Log Output

            with Vertical(id="main_content"):
                yield Label("System Log:")
                yield Log(id="log_window", highlight=True)

    def reset_export_menu(self):
        """Resets the export menu UI to its initial state."""
        # Show the starting buttons
        self.query_one("#btn_export_gui").remove_class("hidden")
        self.query_one("#btn_export_path").remove_class("hidden")

        # Hide the manual input and confirmation buttons
        self.query_one("#input_export_path").add_class("hidden")
        self.query_one("#btn_submit_export_path").add_class("hidden")
        self.query_one("#lbl_export_confirm").add_class("hidden")
        self.query_one("#btn_export_confirm_yes").add_class("hidden")

        # Clear any typed text
        self.query_one("#input_export_path", Input).value = ""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Master event router for the application. Catches every button click
        and routes it to the appropriate navigation or action logic based on the Button's ID.
        """

        log = self.query_one("#log_window", Log)
        btn_id = event.button.id

        # --- Application Exit & Reset ---
        if btn_id == "btn_exit":
            self.exit()

        if btn_id == "btn_restart":
            self.preform_restart()

        # NAVIGATION LOGIC (Menu Swapping)

        # Main Menu -> Load Backup
        if btn_id == "btn_load":
            self.query_one("#main_menu").add_class("hidden")
            self.query_one("#backup_options").remove_class("hidden")
            self.query_one("#lbl_menu_title").update("[b]LOAD BACKUP[/b]")
            log.write_line("[MENU] Select load method...")

        # Load Backup -> Main Menu
        if btn_id == "btn_back_load":
            self.query_one("#backup_options").add_class("hidden")
            self.query_one("#main_menu").remove_class("hidden")
            self.query_one("#lbl_menu_title").update("[b]MAIN MENU[/b]")
            log.write_line("[MENU] Returned to Main Menu...")

        # Main Menu -> Help Options
        if btn_id == "btn_help":
            self.query_one("#main_menu").add_class("hidden")
            self.query_one("#help_options").remove_class("hidden")
            self.query_one("#lbl_menu_title").update("[b]HELP & DOCS[/b]")

        # Help Options -> Main Menu
        if btn_id == "btn_back_help":
            self.query_one("#help_options").add_class("hidden")
            self.query_one("#main_menu").remove_class("hidden")
            self.query_one("#lbl_menu_title").update("[b]MAIN MENU[/b]")
            log.write_line("[MENU] Returned to Main Menu...")

        # ACTION LOGIC (Executing Features)

        # --- Backup Loading ---
        if btn_id == "btn_load_gui":
            selected_folder = gui_pick_folder()
            log.write_line("[INFO] Window opened. Please select a folder.")

            if selected_folder:
                log.write_line(f"\n[USER CHOICE] You chose: {selected_folder}")
                self.run_backup_load(selected_folder)

        # Logic for picking backup using a direct path
        if btn_id == "btn_load_path":
            self.query_one("#input_path").remove_class("hidden")
            self.query_one("#btn_submit_path").remove_class("hidden")

        if btn_id == "btn_submit_path":
            selected_folder = self.query_one("#input_path", Input).value
            if selected_folder:
                self.run_backup_load(selected_folder)

        # --- EXPORT ALL ---
        if btn_id == "btn_export_all":
            if self.backup_service.current_model is None:
                log.write_line(
                    "[!] Error: No backup loaded. Please load a backup first."
                )
            else:
                self.current_export_target = "all albums"
                log.write_line("\n--- EXPORT ALL ---")
                self.query_one("#main_menu").add_class("hidden")
                self.query_one("#export_options").remove_class("hidden")
                self.query_one("#lbl_menu_title").update("[b]EXPORT DESTINATION[/b]")
                self.query_one("#lbl_export_item").update("Destination for: all albums")

        # --- EXPORT DESTINATION HELPER LOGIC ---

        if btn_id == "btn_export_cancel":
            log.write_line("[INFO] Export cancelled.")
            self.reset_export_menu()
            self.query_one("#export_options").add_class("hidden")
            self.query_one("#main_menu").remove_class("hidden")
            self.query_one("#lbl_menu_title").update("[b]MAIN MENU[/b]")

        if btn_id == "btn_export_gui":
            dest_path = gui_pick_folder()
            if not dest_path:
                log.write_line("[INFO] Export cancelled.")
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
                log.write_line("[INFO] Export cancelled.")
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
            target = getattr(self, "current_export_target", "all albums")

            log.write_line(f"[INFO] Executing export for {target} to {dest_path}")

            self.run_export(target, dest_path)

        # --- EXPORT SPECIFIC LOGIC ---
        if btn_id == "btn_specific":
            if not self.backup_service.current_model:
                log.write_line(
                    "[!] Error: No backup loaded. Please load a backup first."
                )
            else:
                available_albums = self.export_service.get_album_list(
                    self.backup_service.current_model
                )
                if not available_albums:
                    log.write_line("[!] Error: No albums found in backup.")
                else:
                    self.query_one("#main_menu").add_class("hidden")
                    self.query_one("#specific_export_options").remove_class("hidden")
                    self.query_one("#lbl_menu_title").update(
                        "[b]EXPORT SPECIFIC ALBUM[/b]"
                    )

                    # Display the list of albums
                    album_text = f"Found {len(available_albums)} albums:\n" + "\n".join(
                        [f" - {a}" for a in available_albums]
                    )
                    self.query_one("#lbl_available_albums").update(album_text)

        if btn_id == "btn_back_specific":
            self.query_one("#specific_export_options").add_class("hidden")
            self.query_one("#main_menu").remove_class("hidden")
            self.query_one("#lbl_menu_title").update("[b]MAIN MENU[/b]")

        if btn_id == "btn_submit_specific_album":
            choice = self.query_one("#input_specific_album", Input).value.strip()
            available_albums = self.export_service.get_album_list(
                self.backup_service.current_model
            )

            if choice.lower() == "cancel":
                log.write_line("[INFO] Export cancelled.")
                self.query_one("#input_specific_album", Input).value = ""
                self.query_one("#specific_export_options").add_class("hidden")
                self.query_one("#main_menu").remove_class("hidden")
                self.query_one("#lbl_menu_title").update("[b]MAIN MENU[/b]")
                return

            if choice in available_albums:
                self.query_one("#input_specific_album", Input).value = ""
                self.current_export_target = choice

                # Hand off to the destination path picker (get_export_destination equivalent)
                self.query_one("#specific_export_options").add_class("hidden")
                self.query_one("#export_options").remove_class("hidden")
                self.query_one("#lbl_menu_title").update("[b]EXPORT DESTINATION[/b]")
                self.query_one("#lbl_export_item").update(
                    f"Destination for: '{choice}'"
                )
            else:
                log.write_line(f"[!] Error: Album '{choice}' does not exist.")

        # -- Settings Logic --

        # Enter Settings Main Menu
        if btn_id == "btn_settings":
            if self.backup_service.current_model is None:
                log.write_line(
                    "[!] Error: You must load a backup before changing settings."
                )
            else:
                self.query_one("#main_menu").add_class("hidden")
                self.query_one("#settings_options").remove_class("hidden")
                self.query_one("#lbl_menu_title").update("[b]SETTINGS[/b]")

        # Back out of Settings
        if btn_id == "btn_back_settings":
            self.query_one("#settings_options").add_class("hidden")
            self.query_one("#main_menu").remove_class("hidden")
            self.query_one("#lbl_menu_title").update("[b]MAIN MENU[/b]")
            log.write_line("[MENU] Returned to Main Menu...")

        # --- BLACKLIST/WHITELIST SUBMENU ---
        if btn_id == "btn_menu_bw":
            self.query_one("#settings_options").add_class("hidden")
            self.query_one("#bw_options").remove_class("hidden")
            self.query_one("#lbl_menu_title").update("[b]BLACKLIST / WHITELIST[/b]")
            # Refresh Labels
            mode, albums = self.settings_service.get_state()
            self.query_one("#lbl_bw_mode").update(f"Mode: {mode}")
            self.query_one("#lbl_bw_list").update(f"List: [{albums}]")

        if btn_id == "btn_bw_switch":
            available_albums = self.export_service.get_album_list(
                self.backup_service.current_model
            )
            msg = self.settings_service.toggle_mode(available_albums)
            log.write_line(f"[BLACKLIST/WHITELIST] {msg}")
            # Refresh Labels after toggle
            mode, albums = self.settings_service.get_state()
            self.query_one("#lbl_bw_mode").update(f"Mode: {mode}")
            self.query_one("#lbl_bw_list").update(f"List: [{albums}]")

        if btn_id == "btn_back_bw":
            self.query_one("#bw_options").add_class("hidden")
            self.query_one("#settings_options").remove_class("hidden")
            self.query_one("#lbl_menu_title").update("[b]SETTINGS[/b]")

        # --- ALBUM MANAGEMENT  ---
        if btn_id == "btn_bw_manage":
            self.query_one("#bw_options").add_class("hidden")
            self.query_one("#album_selection_options").remove_class("hidden")
            self.query_one("#lbl_menu_title").update("[b]ALBUM SELECTION[/b]")

            # Setup dynamic data
            available = self.export_service.get_album_list(
                self.backup_service.current_model
            )
            album_text = "Available Albums in Backup:\n" + "\n".join(
                [f" - {a}" for a in available]
            )
            self.query_one("#lbl_album_avail").update(album_text)

            _, albums = self.settings_service.get_state()
            self.query_one("#lbl_album_current").update(f"Current List: [{albums}]")

        if btn_id == "btn_submit_managed_album":
            name = self.query_one("#input_manage_album", Input).value.strip()
            available = self.export_service.get_album_list(
                self.backup_service.current_model
            )

            if name in available:
                success, msg = self.settings_service.toggle_album(name)
                log.write_line(f"[ALBUM MANAGMENT] {msg}")
                self.query_one("#input_manage_album", Input).value = ""  # Clear input
                # Update the visual list
                _, albums = self.settings_service.get_state()
                self.query_one("#lbl_album_current").update(f"Current List: [{albums}]")
            elif name == "":
                log.write_line("[!] Error: Album name cannot be empty.")
            else:
                log.write_line(
                    f"[!] Error: Album '{name}' does not exist in the current backup."
                )

        if btn_id == "btn_back_album_manage":
            self.query_one("#album_selection_options").add_class("hidden")
            self.query_one("#bw_options").remove_class("hidden")
            self.query_one("#lbl_menu_title").update("[b]BLACKLIST / WHITELIST[/b]")

            # Refresh the list on the previous page just in case
            mode, albums = self.settings_service.get_state()
            self.query_one("#lbl_bw_list").update(f"List: [{albums}]")

        # --- CONVERSION SETTINGS ---
        if btn_id == "btn_menu_conv":
            self.query_one("#settings_options").add_class("hidden")
            self.query_one("#conversion_options").remove_class("hidden")
            self.query_one("#lbl_menu_title").update("[b]CONVERSION SETTINGS[/b]")

            # Update initial button text
            heic_on = "HEIC" in self.conversion_service.enabled
            heic_btn = self.query_one("#btn_toggle_heic", Button)
            heic_btn.label = (
                "1. HEIC → JPG  [✓ ON]" if heic_on else "1. HEIC → JPG  [OFF]"
            )
            heic_btn.variant = "success" if heic_on else "default"

            mov_on = "MOV" in self.conversion_service.enabled
            mov_btn = self.query_one("#btn_toggle_mov", Button)
            mov_btn.label = "2. MOV → MP4  [✓ ON]" if mov_on else "2. MOV → MP4  [OFF]"
            mov_btn.variant = "success" if mov_on else "default"

        if btn_id == "btn_toggle_heic":
            msg = self.conversion_service.toggle("HEIC")
            log.write_line(f"[CONVERSION]{msg}")
            is_on = "HEIC" in self.conversion_service.enabled
            btn = self.query_one("#btn_toggle_heic", Button)
            btn.label = "1. HEIC → JPG  [✓ ON]" if is_on else "1. HEIC → JPG  [OFF]"
            btn.variant = "success" if is_on else "default"

        if btn_id == "btn_toggle_mov":
            msg = self.conversion_service.toggle("MOV")
            log.write_line(f"[CONVERSION]{msg}")
            is_on = "MOV" in self.conversion_service.enabled
            btn = self.query_one("#btn_toggle_mov", Button)
            btn.label = "2. MOV → MP4  [✓ ON]" if is_on else "2. MOV → MP4  [OFF]"
            btn.variant = "success" if is_on else "default"

        if btn_id == "btn_back_conv":
            self.query_one("#conversion_options").add_class("hidden")
            self.query_one("#settings_options").remove_class("hidden")
            self.query_one("#lbl_menu_title").update("[b]SETTINGS[/b]")

        # --- SYMLINK SETTINGS ---
        if btn_id == "btn_menu_symlink":
            self.query_one("#settings_options").add_class("hidden")
            self.query_one("#symlink_options").remove_class("hidden")
            self.query_one("#lbl_menu_title").update("[b]SYMLINK SETTINGS[/b]")

            is_on = self.settings_service.use_symlinks
            status = "✓ ON" if is_on else "OFF"

            self.query_one("#lbl_symlink_status", Label).update(
                f"Current Status: [{status}]"
            )
            self.query_one("#btn_toggle_symlink", Button).variant = (
                "success" if is_on else "default"
            )

        if btn_id == "btn_toggle_symlink":
            msg = self.settings_service.toggle_symlinks()
            log.write_line(f"[SYMLINK] {msg}]")

            is_on = self.settings_service.use_symlinks
            status = "✓ ON" if is_on else "OFF"

            self.query_one("#lbl_symlink_status", Label).update(
                f"Current Status: [{status}]"
            )
            self.query_one("#btn_toggle_symlink", Button).variant = (
                "success" if is_on else "default"
            )

        if btn_id == "btn_back_symlink":
            self.query_one("#symlink_options").add_class("hidden")
            self.query_one("#settings_options").remove_class("hidden")
            self.query_one("#lbl_menu_title").update("[b]SETTINGS[/b]")

        # Smart Album settings

        if btn_id == "btn_menu_smart_album":
            self.query_one("#settings_options").add_class("hidden")
            self.query_one("#smart_album_options").remove_class("hidden")
            self.query_one("#lbl_menu_title").update("[b]SMART ALBUM SETTINGS[/b]")

            # Update status for hidden album
            is_hidden_excluded = "hidden" in self.settings_service.excluded_smart_albums
            hidden_status = "✓ ON" if is_hidden_excluded else "OFF"
            self.query_one("#lbl_hidden_status", Label).update(
                f"Hidden Album: [{hidden_status}]"
            )
            self.query_one("#btn_toggle_hidden", Button).variant = (
                "success" if is_hidden_excluded else "default"
            )

            # Update status for recently deleted album
            is_recently_deleted_excluded = "recently_deleted" in self.settings_service.excluded_smart_albums
            recently_deleted_status = "✓ ON" if is_recently_deleted_excluded else "OFF"
            self.query_one("#lbl_recently_deleted_status", Label).update(
                f"Recently Deleted: [{recently_deleted_status}]"
            )
            self.query_one("#btn_toggle_recently_deleted", Button).variant = (
                "success" if is_recently_deleted_excluded else "default"
            )

        if btn_id == "btn_toggle_hidden":
            # Toggle hidden album exclusion
            msg = self.settings_service.toggle_smart_album_exclusion("hidden")
            log.write_line(f"[SMART ALBUM] {msg}")

            # Update the UI
            is_excluded = "hidden" in self.settings_service.excluded_smart_albums
            status = "✓ ON" if is_excluded else "OFF"

            self.query_one("#lbl_hidden_status", Label).update(
                f"Hidden Album: [{status}]"
            )
            self.query_one("#btn_toggle_hidden", Button).variant = (
                "success" if is_excluded else "default"
            )

        if btn_id == "btn_toggle_recently_deleted":
            # Toggle recently deleted album exclusion
            msg = self.settings_service.toggle_smart_album_exclusion("recently_deleted")
            log.write_line(f"[SMART ALBUM] {msg}")

            # Update the UI
            is_excluded = "recently_deleted" in self.settings_service.excluded_smart_albums
            status = "✓ ON" if is_excluded else "OFF"

            self.query_one("#lbl_recently_deleted_status", Label).update(
                f"Recently Deleted: [{status}]"
            )
            self.query_one("#btn_toggle_recently_deleted", Button).variant = (
                "success" if is_excluded else "default"
            )

        if btn_id == "btn_back_smart_album":
            self.query_one("#smart_album_options").add_class("hidden")
            self.query_one("#settings_options").remove_class("hidden")
            self.query_one("#lbl_menu_title").update("[b]SETTINGS[/b]")

        # --Help Menu ----

        if btn_id == "btn_help_user":
            user_doc = "https://github.com/Gustakev/cs362-class-project/blob/main/documentation/iExtract-User-Documentation.md"
            log.write_line("[INFO] Opening User Documentation in browser...")
            webbrowser.open_new_tab(user_doc)

        if btn_id == "btn_help_dev":
            dev_doc = "https://github.com/Gustakev/cs362-class-project/blob/main/documentation/iExtract-Developer-Documentation.md"
            log.write_line("[INFO] Opening Developer Documentation in browser...")
            webbrowser.open_new_tab(dev_doc)

        if btn_id == "btn_bug":

            issues_url = "https://github.com/Gustakev/cs362-class-project/issues/new"
            log.write_line("[INFO] Opening GitHub Issues for bug report...")
            webbrowser.open_new_tab(issues_url)

        # --- PHOTO DESCRIPTOR ROUTING ---
        if btn_id == "btn_photo_beta":
            self.query_one("#main_menu").add_class("hidden")
            self.query_one("#photo_beta_options").remove_class("hidden")
            self.query_one("#lbl_menu_title").update("[b]PHOTO DESCRIPTOR[/b]")

        if btn_id == "btn_back_photo":
            self.query_one("#photo_beta_options").add_class("hidden")
            self.query_one("#main_menu").remove_class("hidden")
            self.query_one("#lbl_menu_title").update("[b]MAIN MENU[/b]")
            self.query_one("#lbl_photo_caption").update("")

    @work(thread=True)
    def run_backup_load(self, selected_folder):
        """
        Loads the SQLite backup database in a background thread.
        Prevents the UI from freezing during the parsing process.
        """
        log = self.query_one("#log_window")
        pb = self.query_one("#pb_loading")
        options_menu = self.query_one("#backup_options")

        # Show  progress bar
        pb.remove_class("hidden")
        options_menu.disabled = True
        log.write_line("[LOADING] Parsing backup database...")

        #  Call the service
        success, message, icloud_warning = self.backup_service.attempt_load_backup(
            selected_folder
        )
        # Disables menu options while loading backup
        options_menu.disabled = False
        pb.add_class("hidden")
        if success:
            self.call_from_thread(log.write_line, f"[SUCCESS] {message}")
            self.call_from_thread(
                log.write_line, self.backup_service.get_formatted_device_metadata()
            )
            self.call_from_thread(self.query_one("#backup_options").add_class, "hidden")
            self.call_from_thread(self.query_one("#main_menu").remove_class, "hidden")

            if icloud_warning:
                self.call_from_thread(log.write_line, f"[WARNING] {icloud_warning}")
        else:
            self.call_from_thread(log.write_line, f"[ERROR] {message}")

    @work(thread=True)
    def run_export(self, target, dest_path):
        """
        Executes the file extraction and safely updates the UI.
        Relies on the backend ExportService to manage sub-threads.
        """
        log = self.query_one("#log_window")
        pb = self.query_one("#pb_export")
        export_menu = self.query_one("#export_options")

        # Show progress bar and freeze the menu
        self.call_from_thread(pb.remove_class, "hidden")
        self.call_from_thread(setattr, export_menu, "disabled", True)
        self.call_from_thread(
            log.write_line,
            f"[EXPORTING] Executing export for {target} to {dest_path}...",
        )
        self.call_from_thread(pb.update, total=100, progress=0)

        #  Create the safe UI updater
        def update_textual_bar(pct, new_logs=None):
            self.call_from_thread(pb.update, progress=pct)
            if new_logs:
                formatted_logs = [f"  > {msg}" for msg in new_logs]
                self.call_from_thread(log.write_lines, formatted_logs)

        if target == "all albums":
            success, message = self.export_service.export_all(
                self.backup_service.current_model,
                dest_path,
                self.settings_service,
                self.conversion_service,
                ui_callback=update_textual_bar,
            )
        else:
            success, message = self.export_service.export_single_album(
                self.backup_service.current_model,
                dest_path,
                target,
                self.settings_service,
                self.conversion_service,
                ui_callback=update_textual_bar,
            )

        # --- UI Reset and Logging ---
        self.call_from_thread(setattr, export_menu, "disabled", False)
        self.call_from_thread(pb.add_class, "hidden")

        if success:
            self.call_from_thread(log.write_line, f"\n[SUCCESS] {message}\n")
        else:
            self.call_from_thread(log.write_line, f"\n[ERROR] {message}\n")

        self.call_from_thread(self.reset_export_menu)
        self.call_from_thread(export_menu.add_class, "hidden")
        self.call_from_thread(self.query_one("#main_menu").remove_class, "hidden")
        self.call_from_thread(
            self.query_one("#lbl_menu_title").update, "[b]MAIN MENU[/b]"
        )

    @on(DirectoryTree.FileSelected, "#photo_tree")
    def handle_file_selected(self, event: DirectoryTree.FileSelected):
        """Triggered automatically when a file is clicked in the DirectoryTree."""
        selected_path = event.path
        ext = selected_path.suffix.lower()

        if ext in {".jpg", ".jpeg", ".png"}:
            self.query_one("#lbl_photo_caption").update(
                "[b]Loading caption...[/b] (Please wait)"
            )

            self.run_photo_captioner(str(selected_path))
        else:
            self.query_one("#lbl_photo_caption").update(
                f"[!] Unsupported file type: {ext}. Please pick an image."
            )

    @work(thread=True)
    def run_photo_captioner(self, path_str):
        """Background worker to process the image without freezing the TUI."""
        log = self.query_one("#log_window")
        self.call_from_thread(log.write_line, f"[INFO] Processing image: {path_str}")

        try:

            caption = photo_captioner.get_caption(path_str)

            self.call_from_thread(
                self.query_one("#lbl_photo_caption").update,
                f"[b]Caption:[/b] {caption}",
            )

            self.call_from_thread(
                log.write_line, f"[SUCCESS] Caption generated for {path_str}:"
            )
            self.call_from_thread(log.write_line, f"[CAPTION]  {caption}\n")

            image = Image.open(path_str)
            image.show()

        except Exception as e:
            self.call_from_thread(
                self.query_one("#lbl_photo_caption").update,
                f"[!] Error generating caption.",
            )
            self.call_from_thread(log.write_line, f"[ERROR] Caption failed: {str(e)}")

    def preform_restart(self):
        self.backup_service = BackupService()
        self.settings_service = SettingsService()
        self.export_service = ExportService()
        self.conversion_service = ConversionService()

        # Deleting user input in input boxes
        for input_id in [
            "#input_path",
            "#input_manage_album",
            "#input_export_path",
            "#input_specific_album",
        ]:
            self.query_one(input_id, Input).value = ""

        menus_to_hide = [
            "#backup_options",
            "#settings_options",
            "#bw_options",
            "#album_selection_options",
            "#conversion_options",
            "#symlink_options",
            "#help_options",
            "#export_options",
            "#specific_export_options",
            "#photo_beta_options",
            "#hidden_album_options",
        ]
        for menu in menus_to_hide:
            for node in self.query(menu):
                node.add_class("hidden")

        self.query_one("#main_menu").remove_class("hidden")
        self.query_one("#lbl_menu_title").update("[b]MAIN MENU[/b]")

        log = self.query_one("#log_window", Log)
        log.clear()
        log.write_line("[SUCCESS] Application state has been completely restarted.")


def main():
    """
    Program entrypoint.
    """
    app = iExtractApp()
    app.run()


if __name__ == "__main__":
    main()
