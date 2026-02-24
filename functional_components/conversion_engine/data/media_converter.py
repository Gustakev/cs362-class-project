"""
Author: Sam Daughtry (Edited by Kevin Gustafson)
Date: 2026-02-23
Description: Temporarily store converted files.
"""

import os
from PIL import Image
from moviepy import VideoFileClip

from pillow_heif import register_heif_opener
register_heif_opener()


def convert_image(path: str, target_format: str) -> str:
    """Open an image file and save it in the target format.
    Returns the path to the newly created file.
    """
    img = Image.open(path)
    output_file = f"{os.path.splitext(path)[0]}.{target_format.lower()}"
    img.save(output_file)
    return output_file


def convert_video(path: str, target_format: str) -> str:
    """Transcode a video file into the target format using libx264.
    Returns the path to the newly created file.
    """
    video = VideoFileClip(path)
    output_file = f"{os.path.splitext(path)[0]}.{target_format.lower()}"
    video.write_videofile(output_file, codec="libx264")
    return output_file
