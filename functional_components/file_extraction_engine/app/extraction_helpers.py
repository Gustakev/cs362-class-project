"""
Author: Sam Daughtry
Date: 2026-03-01
Description: Helper functions used by the file extraction engine.
"""

import sys
from pathlib import Path
from typing import Dict, List

from functional_components.conversion_engine.app.convert_file import convert_asset
from functional_components.conversion_engine.domain.asset_to_convert import (
    AssetToConvert,
)
from functional_components.file_extraction_engine.domain.collection_ref import (
    CollectionRef,
)


# ---------------------------------------------------------------------------
# Collection / naming helpers
# ---------------------------------------------------------------------------

def get_active_collections(asset, blacklist, album_title_by_uuid) -> List[CollectionRef]:
    """Return a list of collections this asset belongs to honoring the configured blacklist/whitelist."""

    ua_names = {e.name for e in blacklist.current_list if not e.is_NUA}
    nua_names = {e.name for e in blacklist.current_list if e.is_NUA}

    result: List[CollectionRef] = []

    # user albums: resolve UUID -> title via provided map
    for album_uuid in asset.relationships.user_albums:
        title = album_title_by_uuid.get(album_uuid)
        if title is None:
            continue

        if getattr(blacklist, "is_blacklist", True):
            # blacklist mode: include unless explicitly listed
            if title not in ua_names:
                result.append(CollectionRef(title=title, is_nua=False))
        else:
            # whitelist mode: include only when explicitly listed
            if title in ua_names:
                result.append(CollectionRef(title=title, is_nua=False))

    # smart folders
    for nua in asset.relationships.smart_folders:
        if getattr(blacklist, "is_blacklist", True):
            if nua not in nua_names:
                result.append(CollectionRef(title="nua_" + nua, is_nua=True))
        else:
            if nua in nua_names:
                result.append(CollectionRef(title="nua_" + nua, is_nua=True))

    return result


def get_dest_name(asset, resolved_asset) -> str:
    """Return the filename to use when placing a copied/converted asset."""

    stem = Path(asset.original_filename).stem
    if resolved_asset.backup_relative_path != asset.backup_relative_path:
        ext = Path(resolved_asset.backup_relative_path).suffix
    else:
        ext = "." + asset.file_extension.lower()
    return stem + ext


def maybe_convert(asset, convert_type_dict):
    """Convert the asset according to convert_type_dict if necessary."""

    if asset.file_extension.upper() in convert_type_dict:
        result = convert_asset(AssetToConvert(asset, convert_type_dict))
        if result.success:
            return result.converted_asset
        else:
            print(
                f"Conversion failed for {asset.original_filename}: {result.error}",
                file=sys.stderr,
            )
            return asset
    return asset
