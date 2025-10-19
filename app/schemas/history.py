from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class HistoryEntryBase(BaseModel):
    song_id: str

class HistoryEntryCreate(HistoryEntryBase):
    pass

class HistoryEntry(HistoryEntryBase):
    id: UUID
    user_id: str
    position: int  # Añadido campo position
    played_at: datetime

    class Config:
        orm_mode = True