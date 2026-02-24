"""
Author: Kevin Gustafson
Date: 2026-02-23
Description: Reads Manifest.db to locate files within the backup.
"""

from pathlib import Path

from functional_components.sql_cmd_facilitator.data.sqlite_connection_manager import (
    open_db,
)
from functional_components.sql_cmd_facilitator.data.sql_executor import (
    execute_query,
)
from functional_components.sql_cmd_facilitator.data.row_mapper import (
    map_rows,
)


def get_photos_sqlite_path(backup_root: Path) -> Path:
    """Locates Photos.sqlite within the backup by querying Manifest.db.

    Returns the full path to the hashed file on disk.
    """
    manifest_db_path = backup_root / "Manifest.db"

    # Open the Manifest.db file, find Photos.sqlite
    with open_db(manifest_db_path) as conn:
        rows = execute_query(
            conn,
            "SELECT fileID FROM Files WHERE relativePath = ?",
            ("Media/PhotoData/Photos.sqlite",)
        )

    # Save the resulting rows
    results = map_rows(rows)

    # If the Photos.sqlite file cannot be found, print error.
    if not results:
        raise FileNotFoundError(
            "Photos.sqlite not found in Manifest.db. "
            "This iPhone backup may be unsupported or corrupted."
        )

    # Get the path to the Photos.sqlite file and return it.
    file_id = results[0]["fileID"]
    return backup_root / file_id[:2] / file_id
