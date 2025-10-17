from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from .playlist_songs import PlaylistSong

class PlaylistBase(BaseModel):
    name: str
    cover_url: str | None = None
    is_public: bool = False

class PlaylistCreate(PlaylistBase):
    pass

class Playlist(PlaylistBase):
    id: UUID
    owner_id: str
    created_at: datetime
    songs: list[PlaylistSong] = []

    class Config:
        orm_mode = True

class PlaylistWithoutSongs(PlaylistBase):
    id: UUID
    owner_id: str
    created_at: datetime

    class Config:
        orm_mode = True
