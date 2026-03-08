"""
Author: Kevin Gustafson
Date: 2026-02-15
Program Description: Starts the iExtract program.
"""
import sys
from cli_components.main_menu import main


if __name__ == "__main__":
    try :
        print("Starting iExtract... Press Ctrl+C to exit at any time.")
        while True:
            main()
    except KeyboardInterrupt:
        print("\nThank you for using this program. Goodbye.")
        sys.exit(0)
