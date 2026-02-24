"""
Author: Kevin Gustafson
Date: 2026-02-23
Description: Definition for the ConvertTypeDict object.
"""

from typing import Dict

# Maps dictionary entries from the user that say which file types to
#  convert from one type to another.
# Example: { "HEIC": "JPG", "MOV": "MP4" }
ConvertTypeDict = Dict[str, str]
