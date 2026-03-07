"""
Author: Sam Daughtry
Date: 2026-02-28
Description: Definition for the blacklist object.
"""

from typing import List

from dataclasses import dataclass

from .collection_ref import CollectionRef

from typing import ClassVar


@dataclass
class ListEntry:
    name: str
    is_NUA: bool = False

    # Known NUAs matching the canonical names in smart_folders
    _NUAS: ClassVar[set] = {"favorites", "hidden", "selfies", "recently_deleted"}

    def __init__(self, name: str):
        self.name = name.strip()
        self.is_NUA = self.name.lower() in self._NUAS

    def __eq__(self, other):
        if isinstance(other, ListEntry):
            return self.name == other.name
        return False

    def __hash__(self):
        return hash(self.name)


@dataclass
class Blacklist:
    """Tracks a user‑supplied list of collections to exclude or include."""

    current_list: List[ListEntry]
    is_blacklist: bool = True
    