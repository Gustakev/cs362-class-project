"""
Author: Sam Daughtry
Date: 2026-03-01
Description: Main extraction entry point for the file‑extraction engine.
"""

import shutil
from pathlib import Path
from typing import Dict

from functional_components.file_extraction_engine.data.collection_management import (
    deduplicate_assets,
    separate_burst_frames,
    build_album_uuid_to_title_map,
)
from functional_components.file_extraction_engine.data.file_management import (
    non_excl_assets,
    ensure_folder_exists,
    copy_file,
    move_folder,
    copy_folder,
    place_symlink,
    place_folder_symlink,
)

from .extraction_helpers import get_active_collections, get_dest_name, maybe_convert


def run_extraction_engine(
    backup_model,
    blacklist,
    output_root: Path,
    os_supports_symlinks: bool,
    user_set_symlinks: bool,
    convert_type_dict: Dict[str, str],
    progress,
) -> None:
    """Perform the full extraction process."""

    use_symlinks = os_supports_symlinks and user_set_symlinks

    # --- UUID-to-title lookup for user albums ---
    album_title_by_uuid = build_album_uuid_to_title_map(backup_model.albums)

    # --- Deduplicate and partition assets ---
    unique_assets = deduplicate_assets(backup_model.assets)
    burst_groups, asset_list = separate_burst_frames(unique_assets)

    # --- Progress tracking setup ---
    total_units = len(asset_list) + len(burst_groups)
    units_done = 0

    def tick():
        nonlocal units_done
        if total_units == 0:
            return
        units_done += 1
        progress.percent = int((units_done / total_units) * 100)

    # ------------------------------------------------------------------
    # Regular asset loop
    # ------------------------------------------------------------------
    for asset in asset_list:
        active_collections = get_active_collections(
            asset, blacklist, album_title_by_uuid
        )
        collection_count = len(active_collections)

        # already extracted earlier when using symlinks
        if use_symlinks and asset.asset_uuid in non_excl_assets:
            src_path = non_excl_assets[asset.asset_uuid]
            for collection in active_collections:
                dest_folder = ensure_folder_exists(output_root / collection.title)
                place_symlink(src_path, dest_folder)
            tick()
            continue

        # convert/copy source file
        resolved_asset = maybe_convert(asset, convert_type_dict)
        src_path = Path(resolved_asset.backup_relative_path)
        dest_name = get_dest_name(asset, resolved_asset)

        if collection_count == 0 or collection_count > 1:
            if use_symlinks:
                dest_folder = ensure_folder_exists(
                    output_root / "non_exclusive_assets"
                )
                dest_path = copy_file(src_path, dest_folder, dest_name, asset)
                non_excl_assets[asset.asset_uuid] = dest_path

                for collection in active_collections:
                    coll_folder = ensure_folder_exists(
                        output_root / collection.title
                    )
                    place_symlink(dest_path, coll_folder)
            else:
                if collection_count == 0:
                    dest_folder = ensure_folder_exists(
                        output_root / "non_exclusive_assets"
                    )
                    copy_file(src_path, dest_folder, dest_name, asset)
                else:
                    for collection in active_collections:
                        dest_folder = ensure_folder_exists(
                            output_root / collection.title
                        )
                        copy_file(src_path, dest_folder, dest_name, asset)
        else:  # exactly one collection
            dest_folder = ensure_folder_exists(
                output_root / active_collections[0].title
            )
            copy_file(src_path, dest_folder, dest_name, asset)

        tick()

    # ------------------------------------------------------------------
    # Burst group loop
    # ------------------------------------------------------------------
    staging_root = output_root / "staging"

    for burst_uuid, frames in burst_groups.items():
        # choose representative frame for collection membership
        key_frame = next(
            (f for f in frames if f.is_primary_burst_frame), frames[0]
        )
        active_collections = get_active_collections(
            key_frame, blacklist, album_title_by_uuid
        )
        collection_count = len(active_collections)

        # build staging folder and populate with converted frames
        staging_folder = ensure_folder_exists(staging_root / burst_uuid)
        for frame in frames:
            resolved = maybe_convert(frame, convert_type_dict)
            dest_name = get_dest_name(frame, resolved)
            copy_file(
                Path(resolved.backup_relative_path),
                staging_folder,
                dest_name,
                frame,
            )

        # symlink shortcut when already extracted
        if use_symlinks and burst_uuid in non_excl_assets:
            shutil.rmtree(staging_folder)
            src_folder = non_excl_assets[burst_uuid]
            for collection in active_collections:
                dest_folder = ensure_folder_exists(output_root / collection.title)
                place_folder_symlink(src_folder, dest_folder)
            tick()
            continue

        if collection_count == 0 or collection_count > 1:
            if use_symlinks:
                dest_parent = ensure_folder_exists(
                    output_root / "non_exclusive_assets"
                )
                dest_folder = move_folder(staging_folder, dest_parent)
                non_excl_assets[burst_uuid] = dest_folder

                for collection in active_collections:
                    coll_folder = ensure_folder_exists(
                        output_root / collection.title
                    )
                    place_folder_symlink(dest_folder, coll_folder)
            else:
                if collection_count == 0:
                    dest_parent = ensure_folder_exists(
                        output_root / "non_exclusive_assets"
                    )
                    move_folder(staging_folder, dest_parent)
                else:
                    first_dest = ensure_folder_exists(
                        output_root / active_collections[0].title
                    )
                    moved_path = move_folder(staging_folder, first_dest)
                    for collection in active_collections[1:]:
                        dest_parent = ensure_folder_exists(
                            output_root / collection.title
                        )
                        copy_folder(moved_path, dest_parent)
        else:  # exactly one collection
            dest_parent = ensure_folder_exists(
                output_root / active_collections[0].title
            )
            move_folder(staging_folder, dest_parent)

        tick()

    # clean up empty staging root
    if staging_root.exists() and not any(staging_root.iterdir()):
        staging_root.rmdir()

    progress.percent = 100
