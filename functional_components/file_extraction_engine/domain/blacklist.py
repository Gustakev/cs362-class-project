"""
Author: Sam Daughtry
Date: 2026-02-28
Description: Definition for the blacklist object.
"""
from typing import List
from dataclasses import dataclass

from .collection_ref import CollectionRef


@dataclass
class ListEntry:
    name: str
    is_NUA: bool


@dataclass
class Blacklist:
    """Tracks a user‑supplied list of collections to exclude or include."""

    current_list: List[ListEntry]
    is_blacklist: bool = True
    