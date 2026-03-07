"""
Author: Kevin Gustafson
Date: 2026-02-23
Description: Builds Asset domain objects from raw Photos.sqlite data.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import List

from functional_components.backup_locator_and_validator.domain.backup_model import (
    Asset,
    Flags,
    Relationships,
)


# Seconds between Unix epoch (1970-01-01) and Apple epoch (2001-01-01)
APPLE_EPOCH_OFFSET = 978307200

# Maps ZKIND integer values to media_type literals
MEDIA_TYPE_MAP = {
    0: "photo",
    1: "video",
}

# Maps ZKINDSUBTYPE integer values to subtype literals
SUBTYPE_MAP = {
    2: "live_photo_still",
    4: "live_photo_video",
    8: "screenshot",
    16: "portrait",
    32: "panorama",
    64: "slo_mo",
    128: "time_lapse",
    768: "burst_frame",
}


def _convert_apple_epoch(apple_time: float) -> str:
    """Converts Apple epoch timestamp to ISO 8601 string."""
    if apple_time is None:
        return ""
    unix_time = apple_time + APPLE_EPOCH_OFFSET
    return datetime.fromtimestamp(unix_time, tz=timezone.utc).isoformat()

def _get_subtype(zkindsubtype: int) -> str:
    """Maps ZKINDSUBTYPE integer to a subtype literal."""
    if zkindsubtype is None:
        return "standard"
    return SUBTYPE_MAP.get(zkindsubtype, "standard")

def _get_media_type(zkind: int) -> str:
    """Maps ZKIND integer to a media_type literal."""
    return MEDIA_TYPE_MAP.get(zkind, "photo")

def _build_flags(row: dict) -> Flags:
    """Builds a Flags object from raw asset row data."""
    return Flags(
        is_favorite=bool(row.get("ZFAVORITE", 0)),
        is_hidden=bool(row.get("ZHIDDEN", 0)),
        is_recently_deleted=bool(row.get("ZTRASHEDSTATE", 0)),
        # Correctly find selfies.
        is_selfie=row.get("ZDERIVEDCAMERACAPTUREDEVICE") == 1
    )

def _build_relationships(
    asset_pk: int,
    membership_lookup: dict,
) -> Relationships:
    """Builds a Relationships object for an asset."""
    user_albums = membership_lookup.get(asset_pk, [])
    return Relationships(user_albums=user_albums)

def _derive_smart_folders(flags: Flags) -> list:
    """Derives smart_folders list from flags."""
    smart_folders = []
    if flags.is_favorite:
        smart_folders.append("favorites")
    if flags.is_hidden:
        smart_folders.append("hidden")
    if flags.is_recently_deleted:
        smart_folders.append("recently_deleted")
    if flags.is_selfie:
        smart_folders.append("selfies")
    return smart_folders

def build_membership_lookup(raw_memberships: List[dict]) -> dict:
    """Builds a dict mapping asset Z_PK to a list of album UUIDs.

    This is precomputed once and passed into build_assets so we
    don't do a lookup query per asset.
    """
    lookup = {}
    for row in raw_memberships:
        asset_pk = row["asset_pk"]
        album_uuid = row["album_uuid"]
        if asset_pk not in lookup:
            lookup[asset_pk] = []
        lookup[asset_pk].append(album_uuid)
    return lookup

def build_assets(
    raw_assets: List[dict],
    membership_lookup: dict,
    backup_root: Path,
    manifest_conn,
) -> List[Asset]:
    """Converts raw asset rows into Asset domain objects."""
    from functional_components.sql_cmd_facilitator.data.asset_reader import (
        get_file_id_for_asset,
        get_file_id_for_mov_companion,
        get_file_id_fallback,
    )

    assets = []
    skipped = 0

    for row in raw_assets:
        # Resolve the hashed file path from Manifest.db
        original_filename = row.get("ZORIGINALFILENAME") or row.get("ZFILENAME", "")
        directory = row.get("ZDIRECTORY", "")
        relative_path = f"Media/{directory}/{original_filename}"

        try:
            file_id = get_file_id_for_asset(manifest_conn, relative_path)
            backup_relative_path = str(backup_root / file_id[:2] / file_id)
            backup_hashed_filename = file_id
        except FileNotFoundError:
            try:
                file_id = get_file_id_fallback(manifest_conn, original_filename)
                backup_relative_path = str(backup_root / file_id[:2] / file_id)
                backup_hashed_filename = file_id
            except FileNotFoundError:
                skipped += 1
                print(f"SKIPPED: {relative_path}")
                continue

        # Derive file extension from original filename
        file_extension = (
            Path(original_filename).suffix.lstrip(".").upper()
            if original_filename else ""
        )

        # Build flags
        flags = _build_flags(row)

        # Build relationships
        asset_pk = row["Z_PK"]
        relationships = _build_relationships(asset_pk, membership_lookup)

        # Derive smart folders from flags and attach to relationships
        smart_folders = _derive_smart_folders(flags)
        relationships = Relationships(
            user_albums=relationships.user_albums,
            smart_folders=smart_folders,
        )

        # TEMP DEBUG - remove after investigation
        if row.get("ZAVALANCHEUUID") is not None:
            print(
                f"BURST ROW: ZKINDSUBTYPE={row.get('ZKINDSUBTYPE')} "
                f"ZAVALANCHEPICKTYPE={row.get('ZAVALANCHEPICKTYPE')} "
                f"FILE={row.get('ZFILENAME')}"
            )

        assets.append(Asset(
            asset_uuid=row["ZUUID"],
            local_identifier=row["ZUUID"],
            original_filename=original_filename,
            file_extension=file_extension,
            uti_type=row.get("ZUNIFORMTYPEIDENTIFIER") or "",
            creation_date=_convert_apple_epoch(row.get("ZDATECREATED")),
            modification_date=_convert_apple_epoch(row.get("ZMODIFICATIONDATE")),
            timezone_offset="",
            backup_relative_path=backup_relative_path,
            backup_hashed_filename=backup_hashed_filename,
            media_type=_get_media_type(row.get("ZKIND")),
            subtype=_get_subtype(row.get("ZKINDSUBTYPE")),
            live_photo_group_uuid=row.get("ZMEDIAGROUPUUID"),
            burst_uuid=row.get("ZAVALANCHEUUID"),
            is_primary_burst_frame=bool(
                row.get("ZAVALANCHEPICKTYPE") == 2
            ),
            flags=flags,
            relationships=relationships,
        ))

    # Add the index to make the LIKE query fast
    try:
        manifest_conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_files_path ON Files(relativePath)"
        )
    except Exception:
        pass

    # Debug print
    # print(f"Assets skipped (unresolvable in Manifest.db): {skipped}")

    # Second pass: synthesize live_photo_video assets for iOS 26+
    # where companion MOV files exist in Manifest.db but have no ZASSET row.
    live_stills = [
        a for a in assets
        if a.subtype == "live_photo_still"
        and a.live_photo_group_uuid is not None
    ]
    for still in live_stills:
        stem = Path(still.original_filename).stem
        mov_filename = stem + ".MOV"
        try:
            file_id = get_file_id_for_mov_companion(manifest_conn, mov_filename)
            mov_backup_path = str(backup_root / file_id[:2] / file_id)
        except FileNotFoundError:
            continue

        assets.append(Asset(
            asset_uuid=still.asset_uuid + "_mov",
            local_identifier=still.local_identifier + "_mov",
            original_filename=mov_filename,
            file_extension="MOV",
            uti_type="com.apple.quicktime-movie",
            creation_date=still.creation_date,
            modification_date=still.modification_date,
            timezone_offset=still.timezone_offset,
            backup_relative_path=mov_backup_path,
            backup_hashed_filename=file_id,
            media_type="video",
            subtype="live_photo_video",
            live_photo_group_uuid=still.live_photo_group_uuid,
            burst_uuid=None,
            is_primary_burst_frame=False,
            flags=still.flags,
            relationships=still.relationships,
        ))

    return assets
