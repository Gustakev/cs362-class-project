"""
Author: Sam Daughtry
Date: 2026-02-22
Description: Converts proprietary file formats to standard formats.
"""

import os
from PIL import Image
from moviepy import VideoFileClip
import domain.converted_asset as converted_asset
import data.conversion_temp_store as conversion_temp_store

def convert_proprietary_file_format(file_path):
    # Get the file extension
    _, ext = os.path.splitext(file_path)

    # Convert image files
    if ext.lower() in ['.heic']:
        try:
            img = Image.open(file_path)
            output_file = f"{os.path.splitext(file_path)[0]}.png"
            img.save(output_file)
            converted_asset.add_conversion_success(True)
            tempfilepath = conversion_temp_store.store_converted_file(output_file)
            converted_asset.add_converted_asset(tempfilepath)
            
        except Exception as e:
            converted_asset.add_conversion_success(False)
            converted_asset.add_conversion_error(str(e))

    # Convert video files
    elif ext.lower() in ['.mov']:
        try:
            video = VideoFileClip(file_path)
            output_file = f"{os.path.splitext(file_path)[0]}.mp4"
            video.write_videofile(output_file, codec='libx264')
            converted_asset.add_conversion_success(True)
            tempfilepath = conversion_temp_store.store_converted_file(output_file)
            converted_asset.add_converted_asset(tempfilepath)
        except Exception as e:
            converted_asset.add_conversion_success(False)
            converted_asset.add_conversion_error(str(e))