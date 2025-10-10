from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class PlaylistSongBase(BaseModel):
    song_id: UUID

class PlaylistSongCreate(PlaylistSongBase):
    pass

class PlaylistSong(PlaylistSongBase):
    id: UUID
    playlist_id: UUID
    position: int  # Añadir este campo
    added_at: datetime

    class Config:
        orm_mode = True
