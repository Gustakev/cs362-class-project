"""
Author: Sam Daughtry
Date: 2026-02-28
Description: Manages file paths and directories for the file extraction engine.
"""
import os
import shutil
from pathlib import Path
from typing import Dict
from datetime import datetime

non_excl_assets: Dict[str, Path] = {}

def ensure_folder_exists(path: Path) -> Path:
    """Ensure that a folder exists at the given path."""
    path.mkdir(parents=True, exist_ok=True)
    return path

def resolve_free_name(dest_folder: Path, name: str) -> str:
    """Resolve a free name in the destination folder to avoid overwriting existing files."""
    base_name, ext = os.path.splitext(name)
    counter = 1
    new_name = name
    while (dest_folder / new_name).exists():
        new_name = f"{base_name}_{counter}{ext}"
        counter += 1
    return new_name

def copy_file(src_path: Path, dest_folder: Path, dest_name: str, asset) -> Path:
    """Copy a file from src_path to dest_folder with dest_name, ensuring no overwrites."""
    dest_folder = ensure_folder_exists(dest_folder)
    dest_name = resolve_free_name(dest_folder, dest_name)
    dest_path = dest_folder / dest_name
    shutil.copy(src_path, dest_path)
    set_file_times(dest_path, asset.modification_date)
    return dest_path

def move_folder(src_folder: Path, dest_parent: Path) -> Path:
    """Move a folder from src_folder to dest_parent, ensuring no overwrites."""
    dest_parent = ensure_folder_exists(dest_parent)
    dest_folder = dest_parent / src_folder.name
    dest_folder = dest_folder.with_name(resolve_free_name(dest_parent, src_folder.name))
    shutil.move(src_folder, dest_folder)
    return dest_folder

def copy_folder(src_folder: Path, dest_parent: Path) -> Path:
    """Copy a folder from src_folder to dest_parent, ensuring no overwrites."""
    dest_parent = ensure_folder_exists(dest_parent)
    dest_folder = dest_parent / src_folder.name
    dest_folder = dest_folder.with_name(resolve_free_name(dest_parent, src_folder.name))
    shutil.copytree(src_folder, dest_folder)
    return dest_folder

def place_symlink(src_path: Path, dest_folder: Path) -> None:
    """Place a symbolic link to src_path in dest_folder"""
    dest_folder = ensure_folder_exists(dest_folder)
    dest_name = resolve_free_name(dest_folder, src_path.name)
    dest_path = dest_folder / dest_name
    os.symlink(src_path, dest_path)

def place_folder_symlink(src_folder: Path, dest_folder: Path) -> None:
    """Place a symbolic link to src_folder in dest_folder"""
    dest_folder = ensure_folder_exists(dest_folder)
    dest_name = resolve_free_name(dest_folder, src_folder.name)
    dest_path = dest_folder / dest_name
    os.symlink(src_folder, dest_path)

def set_file_times(file_path: Path, modification_date) -> None:
    """Set the modification time of a file to the given date."""
    if isinstance(modification_date, str):
        try:
            dt = datetime.fromisoformat(modification_date)
        except Exception:
            dt = datetime.fromtimestamp(0)
    else:
        dt = modification_date

    mod_time = int(dt.timestamp())
    os.utime(file_path, (mod_time, mod_time))