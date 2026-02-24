"""
Author: Kevin Gustafson
Date: 2026-02-23
Description: Queries Photos.sqlite for album data.
"""

import sqlite3
from typing import List

from functional_components.sql_cmd_facilitator.data.sql_executor import (
    execute_query,
)
from functional_components.sql_cmd_facilitator.data.row_mapper import (
    map_rows,
)


def get_albums(conn: sqlite3.Connection) -> List[dict]:
    """Returns all user-created and burst albums from ZGENERICALBUM."""
    rows = execute_query(
        conn,
        """
        SELECT
            ZUUID,
            ZTITLE,
            ZKIND,
            ZCUSTOMSORTKEY,
            ZCUSTOMSORTASCENDING,
            ZCACHEDCOUNT
        FROM ZGENERICALBUM
        WHERE ZKIND = 2
        ORDER BY ZTITLE
        """
    )
    return map_rows(rows)
