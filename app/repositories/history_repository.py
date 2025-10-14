from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from uuid import UUID
from app import models, schemas

def add_history_entry(db: Session, user_id: UUID, entry: schemas.HistoryEntryCreate):
    # Desplazar todas las posiciones una hacia abajo
    db.query(models.HistoryEntry).filter(
        models.HistoryEntry.user_id == user_id
    ).update({models.HistoryEntry.position: models.HistoryEntry.position + 1})
    
    # Añadir nueva entrada al inicio (posición 1)
    new_entry = models.HistoryEntry(
        user_id=user_id,
        song_id=entry.song_id,
        position=1  # Siempre va al principio
    )
    
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return new_entry

def get_user_history(db: Session, user_id: UUID, skip: int = 0, limit: int = 100):
    return db.query(models.HistoryEntry).filter(
        models.HistoryEntry.user_id == user_id
    ).order_by(models.HistoryEntry.position).offset(skip).limit(limit).all()

def clear_history(db: Session, user_id: UUID):
    result = db.query(models.HistoryEntry).filter(
        models.HistoryEntry.user_id == user_id
    ).delete()
    db.commit()
    return result > 0

def remove_history_entry(db: Session, user_id: UUID, song_id: UUID):
    entry = db.query(models.HistoryEntry).filter(
        models.HistoryEntry.user_id == user_id,
        models.HistoryEntry.song_id == song_id
    ).first()
    
    if not entry:
        return False
    
    # Guardar posición para reordenar
    deleted_position = entry.position
    
    db.delete(entry)
    
    # Actualizar posiciones de entradas posteriores
    db.query(models.HistoryEntry).filter(
        models.HistoryEntry.user_id == user_id,
        models.HistoryEntry.position > deleted_position
    ).update({models.HistoryEntry.position: models.HistoryEntry.position - 1})
    
    db.commit()
    return True