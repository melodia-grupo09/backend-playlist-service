from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from sqlalchemy import and_, or_
from uuid import UUID
from app import models, schemas
import math

def add_history_entry(db: Session, user_id: str, entry: schemas.HistoryEntryCreate):
    db.query(models.HistoryEntry).filter(
        models.HistoryEntry.user_id == user_id
    ).update({models.HistoryEntry.position: models.HistoryEntry.position + 1})

    new_entry = models.HistoryEntry(
        user_id=user_id,
        song_id=entry.song_id,
        song_name=entry.song_name,  # Nuevo campo
        artist_name=entry.artist_name,  # Nuevo campo
        minutos=entry.minutos,
        position=1
    )
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return new_entry

def get_user_history_paginated(db: Session, user_id: str, page: int = 1, limit: int = 10, 
                              search: str = None, artist: str = None):
    """Obtiene el historial con paginación, búsqueda y filtros"""
    
    query = db.query(models.HistoryEntry).filter(
        models.HistoryEntry.user_id == user_id
    )
    
    if search:
        query = query.filter(
            models.HistoryEntry.song_name.ilike(f"%{search}%")
        )
    
    if artist:
        query = query.filter(
            models.HistoryEntry.artist_name.ilike(f"%{artist}%")
        )
    
    total = query.count()
    
    skip = (page - 1) * limit
    total_pages = math.ceil(total / limit) if total > 0 else 1
    
    entries = query.order_by(models.HistoryEntry.position).offset(skip).limit(limit).all()
    
    return {
        "entries": entries,
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages
    }

def get_user_history(db: Session, user_id: str, skip: int = 0, limit: int = 100):
    """Mantener método original para compatibilidad"""
    return db.query(models.HistoryEntry).filter(
        models.HistoryEntry.user_id == user_id
    ).order_by(models.HistoryEntry.position).offset(skip).limit(limit).all()

def clear_history(db: Session, user_id: str):
    result = db.query(models.HistoryEntry).filter(
        models.HistoryEntry.user_id == user_id
    ).delete()
    db.commit()
    return result > 0

def remove_history_entry(db: Session, user_id: str, song_id: str):  # Cambiado de UUID a str
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