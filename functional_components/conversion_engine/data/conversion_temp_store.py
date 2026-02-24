"""
Author: Sam Daughtry (Edited by Kevin Gustafson)
Date: 2026-02-22
Description: Temporarily store converted files.
"""

import tempfile  # Replaced os with tempfile for OS agnosticism!

from pathlib import Path

import shutil


def store_temp_file(source_path: str) -> str:
    """Moves a converted file into a safe temporary directory.
    Returns the full path to the stored temp file."""
    temp_dir = Path(tempfile.mkdtemp(prefix="iconvert_"))
    destination = temp_dir / Path(source_path).name
    shutil.move(source_path, destination)
    return str(destination)
