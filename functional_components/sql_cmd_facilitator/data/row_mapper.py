"""
Author: Kevin Gustafson
Date: 2026-02-23
Description: Converts raw SQLite rows into plain Python dicts.
"""

import sqlite3
from typing import List


def map_rows(rows: List[sqlite3.Row]) -> List[dict]:
    """Converts a list of sqlite3.Row objects into a list of plain dicts.

    Args:
        rows: Raw rows returned by sql_executor.execute_query.

    Returns:
        A list of dicts where each key is a column name.
    """
    return [dict(row) for row in rows]
