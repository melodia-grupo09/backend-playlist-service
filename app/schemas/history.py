from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class HistoryEntryBase(BaseModel):
    song_id: str
    song_name: str | None = None
    artist_name: str | None = None
    minutos: str | None = None

class HistoryEntryCreate(HistoryEntryBase):
    pass

class HistoryEntry(HistoryEntryBase):
    id: UUID
    user_id: str
    position: int
    played_at: datetime

    class Config:   
        orm_mode = True