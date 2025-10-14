from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class LikedSongBase(BaseModel):
    song_id: UUID

class LikedSongCreate(LikedSongBase):
    pass

class LikedSong(LikedSongBase):
    id: UUID
    user_id: UUID
    position: int  # Añadido campo position
    created_at: datetime

    class Config:
        orm_mode = True

class LikedSongPosition(BaseModel):
    song_id: UUID
    position: int