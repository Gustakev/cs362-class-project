"""
Author: Kevin Gustafson
Date: 2026-02-13
Description: Definition for the BackupModel object.
"""

from typing import List, Optional, Literal
from pydantic import BaseModel


class SourceDevice(BaseModel):
    """Keeps the device information in the BackupModel."""
    name: str
    model: str
    ios_version: str


class BackupMetadata(BaseModel):
    """Keeps metadata of the backup itself."""
    backup_uuid: str
    backup_date: str
    is_encrypted: bool
    source_device: SourceDevice


class Flags(BaseModel):
    """Keeps flags that are relevant for determining collection membership."""
    is_favorite: bool = False
    is_hidden: bool = False
    is_recently_deleted: bool = False
    is_selfie: bool = False


class Relationships(BaseModel):
    """Tracks albums and smart albums."""
    user_albums: List[str] = []
    burst_album: Optional[str] = None
    smart_folders: List[
        Literal["favorites", "hidden", "selfies", "recently_deleted"]
    ] = []


class Asset(BaseModel):
    """Tracks an item/asset's data and metadata."""
    asset_uuid: str
    local_identifier: str

    original_filename: str
    file_extension: str
    uti_type: str

    creation_date: str
    modification_date: str
    timezone_offset: str

    backup_relative_path: str
    backup_hashed_filename: str

    media_type: Literal["photo", "video"]
    subtype: Literal[
        "standard",
        "live_photo_still",
        "live_photo_video",
        "burst_frame",
        "panorama",
        "screenshot",
        "portrait",
        "slo_mo",
        "time_lapse"
    ]

    live_photo_group_uuid: Optional[str] = None
    burst_uuid: Optional[str] = None
    is_primary_burst_frame: bool = False

    flags: Flags
    relationships: Relationships


class Album(BaseModel):
    """Tracks an album's data and metadata."""
    album_uuid: str
    title: str
    type: Literal["user", "burst"]
    sort_order: Literal["manual", "date", "none"]
    asset_count: int


class BackupModel(BaseModel):
    """Representation of the entire backup's Photos app contents."""
    backup_metadata: BackupMetadata
    assets: List[Asset]
    albums: List[Album]
