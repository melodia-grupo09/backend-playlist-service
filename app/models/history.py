from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base

class HistoryEntry(Base):
    __tablename__ = "history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    song_id = Column(UUID(as_uuid=True), nullable=False)
    position = Column(Integer, nullable=False)  # Añadido campo position
    played_at = Column(DateTime(timezone=True), server_default=func.now())