"""
Author: Kevin Gustafson
Date: 2026-02-23
Description: Opens, closes, and manages connections to and from an SQL
 database.
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def open_db(db_path: Path):
    """Opens a SQLite database connection and closes it when done.

    Usage Example:
        with open_db(path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT ...")
    """
    if not db_path.exists():
        raise FileNotFoundError(f"Database file not found: {db_path}")

    # Open connection to DB
    conn = sqlite3.connect(db_path)
    # Make every row behave like both a tuple and a dictionary at once
    #  E.g., row["ZUUID"] and row[0] will both work.
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
        