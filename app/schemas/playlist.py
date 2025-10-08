from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class PlaylistBase(BaseModel):
    name: str
    cover_url: str | None = None
    is_public: bool = False

class PlaylistCreate(PlaylistBase):
    pass

class Playlist(PlaylistBase):
    id: UUID
    owner_id: UUID
    created_at: datetime

    class Config:
        orm_mode = True
