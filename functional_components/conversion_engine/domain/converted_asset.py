"""
Author: Kevin Gustafson
Date: 2026-02-16
Description: Definition for the ConvertedAsset object.
"""

from typing import List, Optional, Literal

from pydantic import BaseModel

from functional_components.backup_locator_and_validator.domain.backup_model \
    import Asset


class ConvertedAsset(BaseModel):
    """Describes a converted asset."""
    success: bool  # will be true if the conversion succeeds
    converted_asset: Optional[Asset] = None  # the new asset
    error: Optional[str] = None  # potential error
    