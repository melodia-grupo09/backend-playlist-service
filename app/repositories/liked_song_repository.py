from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from uuid import UUID
from app import models, schemas

def add_liked_song(db: Session, user_id: str, song: schemas.LikedSongCreate):
    existing = db.query(models.LikedSong).filter(
        models.LikedSong.user_id == user_id,
        models.LikedSong.song_id == song.song_id
    ).first()
    
    if existing:
        return existing
    
    max_position = db.query(func.max(models.LikedSong.position)).filter(
        models.LikedSong.user_id == user_id
    ).scalar() or 0
    
    new_liked = models.LikedSong(
        user_id=user_id,
        song_id=song.song_id,
        position=max_position + 1  
    )
    
    db.add(new_liked)
    db.commit()
    db.refresh(new_liked)
    return new_liked

def remove_liked_song(db: Session, user_id: str, song_id: str):  # Cambiado de UUID a str
    liked = db.query(models.LikedSong).filter(
        models.LikedSong.user_id == user_id,
        models.LikedSong.song_id == song_id
    ).first()
    
    if not liked:
        return False
    
    # Guardar la posición para reordenar
    deleted_position = liked.position
    
    db.delete(liked)
    db.commit()
    
    # Reordenar las posiciones de las canciones restantes
    remaining_songs = db.query(models.LikedSong).filter(
        models.LikedSong.user_id == user_id,
        models.LikedSong.position > deleted_position
    ).order_by(models.LikedSong.position).all()
    
    for song in remaining_songs:
        song.position -= 1
    
    db.commit()
    return True

def get_user_liked_songs(db: Session, user_id: str, skip: int = 0, limit: int = 100):
    return db.query(models.LikedSong).filter(
        models.LikedSong.user_id == user_id
    ).order_by(models.LikedSong.position).offset(skip).limit(limit).all()

def update_position(db: Session, user_id: str, song_id: UUID, new_position: int):
    liked = db.query(models.LikedSong).filter(
        models.LikedSong.user_id == user_id,
        models.LikedSong.song_id == song_id
    ).first()
    
    if not liked:
        return False
    
    current_position = liked.position
    
    if current_position == new_position:
        return True
    
    if current_position < new_position:
        db.query(models.LikedSong).filter(
            models.LikedSong.user_id == user_id,
            models.LikedSong.position > current_position,
            models.LikedSong.position <= new_position
        ).update({models.LikedSong.position: models.LikedSong.position - 1})
    else:
        db.query(models.LikedSong).filter(
            models.LikedSong.user_id == user_id,
            models.LikedSong.position >= new_position,
            models.LikedSong.position < current_position
        ).update({models.LikedSong.position: models.LikedSong.position + 1})
    
    liked.position = new_position
    db.commit()
    
    return True

def reorder_songs(db: Session, user_id: str, song_positions: list[schemas.LikedSongPosition]):
    try:
        for song_pos in song_positions:
            liked = db.query(models.LikedSong).filter(
                models.LikedSong.user_id == user_id,
                models.LikedSong.song_id == song_pos.song_id
            ).first()
            
            if not liked:
                return False
        for song_pos in song_positions:
            db.query(models.LikedSong).filter(
                models.LikedSong.user_id == user_id,
                models.LikedSong.song_id == song_pos.song_id
            ).update({models.LikedSong.position: song_pos.position})
        
        db.commit()
        return True
        
    except Exception:
        db.rollback()
        return False

def is_song_liked_by_user(db: Session, user_id: str, song_id: str) -> bool:
    """
    Devuelve True si la canción está en los liked_songs del usuario, False si no.
    """
    return db.query(models.LikedSong).filter(
        models.LikedSong.user_id == user_id,
        models.LikedSong.song_id == song_id
    ).first() is not None