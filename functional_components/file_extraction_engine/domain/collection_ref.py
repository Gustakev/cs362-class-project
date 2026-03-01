"""
Author: Sam Daughtry
Date: 2026-02-28
Description: Definition for the CollectionRef object.
"""
from dataclasses import dataclass


@dataclass
class CollectionRef:
    title: str
    is_nua: bool