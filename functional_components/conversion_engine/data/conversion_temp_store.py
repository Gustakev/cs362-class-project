"""
Author: Sam Daughtry
Date: 2026-02-22
Description: Temporary data store for converted file paths during the conversion process.
"""
import os
from pathlib import Path


def store_in_directory(file):
    temp_dir = Path("conversions")
    temp_dir.mkdir(exist_ok=True)
    
    # Move the file to the temporary directory
    destination = temp_dir / os.path.basename(file)
    os.rename(file, destination)
    
    return str(destination)