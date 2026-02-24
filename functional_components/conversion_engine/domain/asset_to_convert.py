"""
Author: Kevin Gustafson
Date: 2026-02-23
Description: Definition for the AssetToConvert object.
"""

from typing import List, Optional, Literal

from pydantic import BaseModel

from functional_components.backup_locator_and_validator.domain.backup_model \
    import Asset

from functional_components.conversion_engine.domain.convert_type_dict \
    import ConvertTypeDict


class AssetToConvert(BaseModel):
    """Describes an asset needing conversion."""
    # If there is a dictionary entry in this like HEIC : JPG, that means
    #  convert HEIC to JPEG. The extraction engine will identify this using
    #  the same dict, then create this object with the dict set to this dict
    #  and the asset_to_convet set to the Asset that needs to be converted,
    #  and it will then pass this whole object into the app layer logic
    #  of the conversion engine.
    asset_to_convert: Asset
    convert_type_dict: ConvertTypeDict
    