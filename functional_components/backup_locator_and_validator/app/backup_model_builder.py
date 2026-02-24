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
    SourceDevice,
    Asset,
    Album,
    Flags,
    Relationships
)

from functional_components.backup_locator_and_validator.domain. \
    backup_model_result import BackupModelResult

from functional_components.backup_locator_and_validator.data.get_device_info \
    import get_device_info

from functional_components.backup_locator_and_validator.data. \
    get_device_manifest import get_encryption_status


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

    # Make the BackupModel object
    backup_model = BackupModel(
        backup_metadata=BackupMetadata(
            backup_uuid=raw_info["GUID"],
            backup_date=raw_info["Last Backup Date"].isoformat(),
            is_encrypted=is_encrypted,
            source_device=device
        ),
        assets=[],
        albums=[]
    )

    # Debug prints
    # print(f"{backup_model.backup_metadata.backup_date}")
    # print(f"{backup_model.backup_metadata.is_encrypted}")

    return BackupModelResult(
        success=True, backup_model=backup_model
    )
