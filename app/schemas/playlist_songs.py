from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class PlaylistSongBase(BaseModel):
    song_id: str

class PlaylistSongCreate(PlaylistSongBase):
    pass

class PlaylistSong(PlaylistSongBase):
    id: UUID
    playlist_id: UUID
    position: int
    added_at: datetime

    class Config:
        orm_mode = True

class PlaylistSongPositionUpdate(BaseModel):
    song_id: str
    position: int