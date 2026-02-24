"""
Author: Kevin Gustafson
Date: 2026-02-23
Description: Inspects the Photos.sqlite schema to discover dynamic
    table and column names that vary across iOS versions.
"""

import sqlite3


def find_album_asset_join_table(conn: sqlite3.Connection) -> str:
    """Finds the album-to-asset join table name dynamically.

    In Photos.sqlite, this table is named Z_<number>ASSETS and changes
    across iOS versions (e.g. Z_26ASSETS, Z_33ASSETS, Z_42ASSETS).
    """
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
    tables = [row["name"] for row in rows]

    matches = [
        t for t in tables
        if t.startswith("Z_") and "ASSET" in t and t != "ZASSET"
    ]

    if not matches:
        raise RuntimeError(
            "Could not find album-to-asset join table in Photos.sqlite. "
            "The backup may be from an unsupported iOS version."
        )

    return matches[0]


def find_join_table_columns(conn: sqlite3.Connection, join_table: str) -> dict:
    """Finds the correct column names inside the join table dynamically.

    Returns a dict with keys: album_fk, asset_fk, sort_col.
    """
    rows = conn.execute(
        f"PRAGMA table_info({join_table})"
    ).fetchall()
    cols = [row["name"] for row in rows]

    try:
        album_fk = next(c for c in cols if c.endswith("ALBUMS"))
        asset_fk = next(
            c for c in cols
            if c.endswith("ASSETS") and not c.startswith("Z_FOK")
        )
        sort_col = next(c for c in cols if c.startswith("Z_FOK"))
    except StopIteration:
        raise RuntimeError(
            f"Could not identify expected columns in {join_table}. "
            f"Found columns: {cols}"
        )

    return {
        "album_fk": album_fk,
        "asset_fk": asset_fk,
        "sort_col": sort_col,
    }
