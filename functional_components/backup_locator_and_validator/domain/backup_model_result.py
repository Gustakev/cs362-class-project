"""
Author: Kevin Gustafson
Date: 2026-02-15
Description: The Result that contains the BackupModel and status.
"""

from typing import List, Optional, Literal
from pydantic import BaseModel

from functional_components.backup_locator_and_validator.domain.backup_model \
    import BackupModel


class BackupModelResult(BaseModel):
    """Represents the BackupModel and whether it was created or not."""
    success: bool
    backup_model: Optional[BackupModel] = None
    error: Optional[str] = None
