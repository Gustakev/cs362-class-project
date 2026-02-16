"""
Author: Kevin Gustafson
Date: 2026-02-15
Description: Process to build the BackupModel.
"""

from pathlib import Path
import plistlib

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


def build_device(backup_root: Path) -> SourceDevice:
    """Builds and returns the device object."""
    raw_info = get_device_info(backup_root)
    device = SourceDevice(
        name = raw_info["Device Name"],  # name
        model = raw_info["Product Type"],  # model
        ios_version = raw_info["Product Version"]  # ios_version
    )
    return device


def build_backup_model(backup_root: Path) -> BackupModelResult:
    """The function in which the whole backup model is built."""

    """Create the device object."""
    try:
        device = build_device(backup_root)
    except Exception as e:
        return BackupModelResult(
            success = False,
            error=f"Failed loading device info.: {e}"
        )
    
    """Make the BackupModel object."""
    backup_model = BackupModel(
    backup_metadata=BackupMetadata(
        backup_uuid="test",
        backup_date="test",
        is_encrypted=False,
        source_device=device
    ),
    assets=[],
    albums=[]
)

    return BackupModelResult(
        success = True, backup_model = backup_model
    )
