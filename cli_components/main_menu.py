"""
Author: Kevin Gustafson
Date: 1/29/2025
Program Description: Command line interface for iExtract.
"""
##############
# Constants: #
##############


############
# Imports: #
############
# For error handling.
import sys
# Necessary for GUI dialogue, reducing complexity for the user.
import tkinter as tk
from tkinter import filedialog

#########################
# Function Definitions: #
#########################
#||||||||||||||||||||||||||#
# Generic Function Header: #
# Name: 
# Purpose: 
# Inputs: 
# Outputs: 
#||||||||||||||||||||||||||#

# Name: guiPickFolder
# Purpose: This helper allows a user to pick a folder using their system's built-in GUI folder picker.
# Inputs: N/A
# Outputs: (folder : string): Folder path string
def guiPickFolder():
    try:
         # Obtain folder string and return it:
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        root.update()
        folder = filedialog.askdirectory(title="Select a folder")
        return folder
    except tk.TclError:
        # If there is no GUI on the OS:
        print("Error: GUI folder selection is not available on this system.", file=sys.stderr)
        return None

# Name: loadBackupMenu
# Purpose: Submenu for choosing how to pick the backup folder.
def loadBackupMenu():
    while True:
        # Ask user which way they want to select their folder:
        print("*** Instructions: Enter the number corresponding to the choices below. ***\n")
        print("1. Load iPhone Backup Folder Via GUI")
        print("2. Load iPhone Backup Folder By Entering File Path")
        print("3. Go Back")

        # Collecting which way the user wants to choose their folder:
        folderPickerMethod = input("\nChoose an option: ")
        print("")

        # Handling their choice:
        if folderPickerMethod == "1":
            selectedFolder = guiPickFolder()
            if not selectedFolder:
                print("This system does not support GUI folder selection.\n")
                continue
            print("You chose:", selectedFolder)
            print("\n")
            # TODO: Go into loading the backup now. If the backup fails to load, print error and do 'continue' to go
            #  ask the user how they would like to choose their backup folder again.
            return # Prints successful load message and returns to main menu if successful load happens.
        elif folderPickerMethod == "2":
            selectedFolder = input("Enter the path to your iPhone backup folder: ")
            print("")
            print("You chose:", selectedFolder)
            print("\n")
            # TODO: Go into loading the backup now. If the backup fails to load, print error and do 'continue' to go
            #  ask the user how they would like to choose their backup folder again.
        elif folderPickerMethod == "3":
            print("\nGoing back...\n")
            return # Return to main menu.
        else:
            print("Error: Invalid input. Choose one of the displayed options.", file=sys.stderr)
            print("")
            # Naturally restarts loop...

# Name: mainMenu
# Purpose: This is the main program command line interface loop.
# Inputs: N/A
# Outputs: N/A
def mainMenu():
    while True:
        # Print options:
        print("\n=========================== iExtract Main Menu ===========================")
        print("\n*** Instructions: Enter the number corresponding to the choices below. ***\n")
        print("1. Load iPhone Backup Folder")
        print("2. Export All Camera Roll Media")
        print("3. Export Specific Camera Roll Media")
        print("4. Settings")
        print("5. Exit")

        # User options logic:
        mainMenuChoice = input("\nChoose an option: ")
        print("")

        # Branches:
        if mainMenuChoice == "1":
            loadBackupMenu()
        elif mainMenuChoice == "2":
            print("Export All Camera Roll Media (not implemented yet)\n")
        elif mainMenuChoice == "3":
            print("Export Specific Camera Roll Media (not implemented yet)\n")
        elif mainMenuChoice == "4":
            print("Settings (not implemented yet)\n")
        elif mainMenuChoice == "5":
            print("Thank you for using this program. Goodbye.")
            return
        else:
            print("Error: Invalid input. Choose one of the displayed options.", file=sys.stderr)

def backupMenu():
    print("")

def exportAllMenu():
    print("")

def exportSpecificMenu():
    print("")

def settingsMenu():
    print("")

def inputValidation():
    print("")

def progressDisplay():
    print("")

def errorDisplay():
    print("")

# Name: main
# Purpose: This is the program entrypoint.
# Inputs: N/A
# Outputs: N/A
def main():
    # Load the main menu loop:
    mainMenu()

# Entrypoint for program:
main()
