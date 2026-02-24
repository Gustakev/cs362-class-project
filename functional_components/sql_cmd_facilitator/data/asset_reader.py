"""
Author: Kevin Gustafson
Date: 2026-02-23
Description: Queries Photos.sqlite for asset data.
"""

import sqlite3
from typing import List

from functional_components.sql_cmd_facilitator.data.sql_executor import (
    execute_query,
)
from functional_components.sql_cmd_facilitator.data.row_mapper import (
    map_rows,
)


def get_assets(conn: sqlite3.Connection) -> List[dict]:
    """Returns all assets from ZASSET joined with ZADDITIONALASSETATTRIBUTES."""
    rows = execute_query(
        conn,
        """
        SELECT
            ZASSET.ZUUID,
            ZASSET.Z_PK,
            ZASSET.ZFILENAME,
            ZASSET.ZDIRECTORY,
            ZASSET.ZUNIFORMTYPEIDENTIFIER,
            ZASSET.ZDATECREATED,
            ZASSET.ZMODIFICATIONDATE,
            ZASSET.ZKIND,
            ZASSET.ZKINDSUBTYPE,
            ZASSET.ZFAVORITE,
            ZASSET.ZHIDDEN,
            ZASSET.ZTRASHEDSTATE,
            ZASSET.ZAVALANCHEUUID,
            ZASSET.ZAVALANCHEPICKTYPE,
            ZASSET.ZMEDIAGROUPUUID,
            ZADDITIONALASSETATTRIBUTES.ZORIGINALFILENAME
        FROM ZASSET
        LEFT JOIN ZADDITIONALASSETATTRIBUTES
            ON ZADDITIONALASSETATTRIBUTES.ZASSET = ZASSET.Z_PK
        """
    )
    return map_rows(rows)


def get_asset_album_memberships(
    conn: sqlite3.Connection,
    join_table: str,
    album_fk: str,
    asset_fk: str,
) -> List[dict]:
    """Returns all asset-to-album mappings from the join table."""
    rows = execute_query(
        conn,
        f"""
        SELECT
            {join_table}.{asset_fk} AS asset_pk,
            ZGENERICALBUM.ZUUID AS album_uuid
        FROM {join_table}
        JOIN ZGENERICALBUM
            ON ZGENERICALBUM.Z_PK = {join_table}.{album_fk}
        WHERE ZGENERICALBUM.ZKIND = 2
        """
    )
    return map_rows(rows)


def get_file_id_for_asset(
    conn: sqlite3.Connection,
    relative_path: str,
) -> str:
    """Queries Manifest.db for the hashed fileID of a given relative path."""
    rows = execute_query(
        conn,
        "SELECT fileID FROM Files WHERE relativePath = ?",
        (relative_path,)
    )
    results = map_rows(rows)
    if not results:
        raise FileNotFoundError(
            f"No file found in Manifest.db for path: {relative_path}"
        )
    return results[0]["fileID"]
