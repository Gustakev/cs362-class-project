"""
Author: Kevin Gustafson
Date: 2026-02-15
Program Description: Starts the iExtract program.
"""

import warnings

warnings.filterwarnings("ignore", message=".*urllib3.*")
warnings.filterwarnings("ignore", message=".*chardet.*")
warnings.filterwarnings("ignore", message=".*charset_normalizer.*")
warnings.filterwarnings("ignore", message=".*character detection.*")

import sys

from cli_components.main_menu import main as cli_main

from cli_components.textual_main_menu import iExtractApp


def launch_prompt():
    """Prompts the user to choose an interface before starting the program."""
    while True:
        print("\033[36m" + "==================================================" + "\033[0m")
        print("\033[36m" + "               Welcome to iExtract                " + "\033[0m")
        print("\033[36m" + "==================================================\n" + "\033[0m")
        
        print("Please select an interface:")
        print("1. Standard CLI (Stable)")
        print("2. Textual Dashboard (Beta)")
        print("3. Exit")
        
        choice = input("\nSelect an option: ").strip()
        
        if choice == "1":
            print("\nStarting Standard CLI...\n")
            cli_main() 
            break
            
        elif choice == "2":
            print("\nStarting Textual Dashboard (Beta)...")
            app = iExtractApp()
            app.run() 
            break
            
        elif choice == "3":
            print("Goodbye.")
            sys.exit()
            
        else:
            print("\033[31m[!] Invalid choice. Please enter 1, 2, or 3.\033[0m\n")


if __name__ == "__main__":
    try :
        print(f"\033[33m" + "\nStarting iExtract... Press Ctrl+C to exit at any time." + "\033[0m")
        while True:
            launch_prompt()
    except KeyboardInterrupt:
        print("\nThank you for using this program. Goodbye.")
        sys.exit(0)
    