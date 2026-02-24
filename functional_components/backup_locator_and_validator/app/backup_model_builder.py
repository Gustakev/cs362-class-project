"""
Author: Kevin Gustafson
Date: 2026-02-15
Description: Process to build the BackupModel.
"""

from pathlib import Path

from functional_components.backup_locator_and_validator.domain.backup_model \
    import (
    BackupModel,
    BackupMetadata,
    SourceDevice
)

from functional_components.backup_locator_and_validator.domain. \
    backup_model_result import BackupModelResult

from functional_components.backup_locator_and_validator.data.get_device_info \
    import get_device_info

from functional_components.backup_locator_and_validator.data. \
    get_device_manifest import get_encryption_status

from functional_components.sql_cmd_facilitator.data.manifest_db_reader import (
    get_photos_sqlite_path,
)

from functional_components.sql_cmd_facilitator.data.sqlite_connection_manager import (
    open_db,
)

from functional_components.sql_cmd_facilitator.app.schema_inspector import (
    find_album_asset_join_table,
    find_join_table_columns,
)

from functional_components.sql_cmd_facilitator.data.album_reader import (
    get_albums,
)

from functional_components.sql_cmd_facilitator.app.album_builder import (
    build_albums,
)

from functional_components.sql_cmd_facilitator.data.asset_reader import (
    get_assets,
    get_asset_album_memberships,
)

from functional_components.sql_cmd_facilitator.app.asset_builder import (
    build_assets,
    build_membership_lookup,
)


def build_device(raw_info: dict) -> SourceDevice:
    """Builds and returns the device object."""
    device = SourceDevice(
        name=raw_info["Device Name"],
        model=raw_info["Product Type"],
        ios_version=raw_info["Product Version"]
    )
    return device


def build_backup_model(backup_root: Path) -> BackupModelResult:
    """The function in which the whole backup model is built."""

    # Read source files once
    try:
        raw_info = get_device_info(backup_root)
    except Exception as e:
        return BackupModelResult(
            success=False,
            error=f"Failed loading device info: {e}"
        )

    try:
        is_encrypted = get_encryption_status(backup_root)
    except Exception as e:
        return BackupModelResult(
            success=False,
            error=f"Failed reading Manifest.plist: {e}"
        )

    # If encrypted, fail immediately
    if is_encrypted:
        return BackupModelResult(
            success=False,
            error="Backup is encrypted. Please provide an unencrypted backup."
        )

    # Build the device object from the already-loaded raw_info
    try:
        device = build_device(raw_info)
    except Exception as e:
        return BackupModelResult(
            success=False,
            error=f"Failed building device object: {e}"
        )

    # Locate Photos.sqlite via Manifest.db
    try:
        photos_sqlite_path = get_photos_sqlite_path(backup_root)
    except Exception as e:
        return BackupModelResult(
            success=False,
            error=f"Failed locating Photos.sqlite: {e}"
        )

    # Query Photos.sqlite and Manifest.db to build assets and albums
    try:
        manifest_db_path = backup_root / "Manifest.db"

        with open_db(photos_sqlite_path) as photos_conn, \
             open_db(manifest_db_path) as manifest_conn:

            # Discover dynamic schema
            join_table = find_album_asset_join_table(photos_conn)
            join_cols = find_join_table_columns(photos_conn, join_table)

            # Build albums
            raw_albums = get_albums(photos_conn)
            albums = build_albums(raw_albums)

            # Build assets
            raw_assets = get_assets(photos_conn)
            raw_memberships = get_asset_album_memberships(
                photos_conn,
                join_table,
                join_cols["album_fk"],
                join_cols["asset_fk"],
            )
            membership_lookup = build_membership_lookup(raw_memberships)
            assets = build_assets(
                raw_assets,
                membership_lookup,
                backup_root,
                manifest_conn,
            )

    except Exception as e:
        return BackupModelResult(
            success=False,
            error=f"Failed building assets and albums: {e}"
        )

    # Make the BackupModel object
    backup_model = BackupModel(
        backup_metadata=BackupMetadata(
            backup_uuid=raw_info["GUID"],
            backup_date=raw_info["Last Backup Date"].isoformat(),
            is_encrypted=is_encrypted,
            source_device=device
        ),
        assets=assets,
        albums=albums
    )

    # Debug prints
    # print(f"{backup_model.backup_metadata.backup_uuid}")
    # print(f"{backup_model.backup_metadata.backup_date}")
    # print(f"{backup_model.backup_metadata.is_encrypted}")
    # print(f"Albums loaded: {len(backup_model.albums)}")
    # print(f"Assets loaded: {len(backup_model.assets)}")

    return BackupModelResult(
        success=True, backup_model=backup_model
    )
