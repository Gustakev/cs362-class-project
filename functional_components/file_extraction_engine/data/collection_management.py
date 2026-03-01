"""
Author: Sam Daughtry
Date: 2026-02-28
Description: Manages assets collections
"""

from typing import List, Dict
from functional_components.backup_locator_and_validator.domain.backup_model import Asset, Album

def deduplicate_assets(assets: List[Asset]) -> List[Asset]:
    """Deduplicates a list of assets based on their unique identifiers."""
    seen = set()
    unique_assets = []
    
    for asset in assets:
        if asset.asset_uuid not in seen:
            seen.add(asset.asset_uuid)
            unique_assets.append(asset)
    
    return unique_assets

def separate_burst_frames(assets: List[Asset]) -> tuple[Dict, List]:
    """Separates burst frames from the main asset list. """
    burst_groups: Dict[str, list] = {}
    asset_list: List[Asset] = []
    for asset in assets:
        if asset.subtype == "burst_frame" and asset.burst_uuid is not None:
            burst_groups.setdefault(asset.burst_uuid, []).append(asset)
        else:
            asset_list.append(asset)
    return burst_groups, asset_list

def build_album_uuid_to_title_map(backup_model_albums) -> Dict[str, str]:
    """Builds a mapping from album UUIDs to their corresponding titles."""
    return {album.album_uuid: album.title for album in backup_model_albums if album.type == "user"}
    