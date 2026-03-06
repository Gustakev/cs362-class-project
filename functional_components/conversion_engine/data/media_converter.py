"""
Author: Sam Daughtry (Edited by Kevin Gustafson)
Date: 2026-03-06
Description: Converts media files to target formats.
"""

import os

import subprocess

from pathlib import Path

from PIL import Image

from pillow_heif import register_heif_opener


register_heif_opener()


def _get_temp_dir(temp_dir) -> Path:
    """Use provided temp_dir, creating it if necessary."""
    p = Path(temp_dir)
    p.mkdir(parents=True, exist_ok=True)
    return p


def convert_image(path: str, target_format: str, temp_dir) -> str:
    """Open an image file and save it in the target format.
    Returns the path to the newly created file.
    """
    out_dir = _get_temp_dir(temp_dir)
    output_file = str(out_dir / (Path(path).stem + "." + target_format.lower()))
    img = Image.open(path)
    img.save(output_file)
    return output_file


def convert_video(path: str, target_format: str, temp_dir) -> str:
    """Transcode a video file using ffmpeg directly.
    Returns the path to the newly created file.
    """
    out_dir = _get_temp_dir(temp_dir)
    output_file = str(out_dir / (Path(path).stem + "." + target_format.lower()))
    result = subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", path,
            "-c:v", "libx264",
            "-c:a", "aac",
            "-loglevel", "error",
            output_file,
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
    return output_file
