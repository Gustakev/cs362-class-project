"""
Author: Kevin Gustafson
Date: 2026-02-23
Description: Executes SQL queries against an open SQLite connection.
"""

import sqlite3
from typing import List


def execute_query(conn: sqlite3.Connection, query: str, params: tuple = ()) -> List[sqlite3.Row]:
    """Executes a SQL query and returns all resulting rows.

    Args:
        conn: An open SQLite connection.
        query: The SQL query string to execute.
        params: Optional tuple of parameters to bind to the query.

    Returns:
        A list of sqlite3.Row objects.
    """
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()
    except sqlite3.OperationalError as e:
        raise RuntimeError(f"Query failed: {e}\nQuery was: {query}")
        