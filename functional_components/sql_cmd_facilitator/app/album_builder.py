"""
Author: Kevin Gustafson
Date: 2026-02-23
Description: Builds Album domain objects from raw Photos.sqlite data.
"""

from typing import List

from functional_components.backup_locator_and_validator.domain.backup_model import (
    Album,
)


def _get_sort_order(row: dict) -> str:
    """Derives sort_order from ZCUSTOMSORTKEY and ZCUSTOMSORTASCENDING."""
    if row.get("ZCUSTOMSORTKEY"):
        return "manual"
    if row.get("ZCUSTOMSORTASCENDING") is not None:
        return "date"
    return "none"


def build_albums(raw_albums: List[dict]) -> List[Album]:
    """Converts raw album rows into Album domain objects."""
    albums = []
    for row in raw_albums:
        albums.append(Album(
            album_uuid=row["ZUUID"],
            title=row["ZTITLE"] or "",
            type="user",
            sort_order=_get_sort_order(row),
            asset_count=row["ZCACHEDCOUNT"] or 0,
        ))

    return albums
