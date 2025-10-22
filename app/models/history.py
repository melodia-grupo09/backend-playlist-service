from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base

class HistoryEntry(Base):
    __tablename__ = "history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=False, index=True)
    song_id = Column(String, nullable=False)
    minutos = Column(String, nullable=True)
    position = Column(Integer, nullable=False)
    played_at = Column(DateTime(timezone=True), server_default=func.now())