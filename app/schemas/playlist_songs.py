from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class PlaylistSongBase(BaseModel):
    song_id: UUID
    position: int

class PlaylistSongCreate(PlaylistSongBase):
    pass

class PlaylistSong(PlaylistSongBase):
    id: UUID
    playlist_id: UUID
    added_at: datetime

    class Config:
        orm_mode = True
