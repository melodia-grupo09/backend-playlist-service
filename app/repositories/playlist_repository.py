from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from uuid import UUID
from app import models, schemas

def create_playlist(db: Session, playlist: schemas.PlaylistCreate, user_id: UUID):
    new_playlist = models.Playlist(**playlist.dict(), owner_id=user_id)
    db.add(new_playlist)
    db.commit()
    db.refresh(new_playlist)
    return new_playlist

def get_playlists(db: Session, user_id: UUID | None = None):
    query = db.query(models.Playlist)
    if user_id:
        query = query.filter(models.Playlist.owner_id == user_id)
    return query.all()

def get_playlist(db: Session, playlist_id: UUID):
    return db.query(models.Playlist).filter(models.Playlist.id == playlist_id).first()

def add_song(db: Session, playlist_id: UUID, song: schemas.PlaylistSongCreate):
    # Verificar que existe la playlist
    playlist = get_playlist(db, playlist_id)
    if not playlist:
        return None
    
    # Calcular la siguiente posición
    max_position = db.query(func.max(models.PlaylistSong.position)).filter(
        models.PlaylistSong.playlist_id == playlist_id
    ).scalar() or 0
    
    # Crear la nueva canción con posición calculada
    new_song = models.PlaylistSong(
        playlist_id=playlist_id,
        song_id=song.song_id,
        position=max_position + 1
    )
    
    db.add(new_song)
    db.commit()
    db.refresh(new_song)
    return new_song

def remove_song(db: Session, playlist_id: UUID, song_id: UUID):
    # Cambiar el filtro para buscar por song_id en lugar de id
    song = db.query(models.PlaylistSong).filter(
        models.PlaylistSong.song_id == song_id,
        models.PlaylistSong.playlist_id == playlist_id
    ).first()
    
    if not song:
        return False
    
    db.delete(song)
    db.commit()
    
    # Reordenar las posiciones de las canciones restantes
    remaining_songs = db.query(models.PlaylistSong).filter(
        models.PlaylistSong.playlist_id == playlist_id
    ).order_by(models.PlaylistSong.position).all()
    
    for i, remaining_song in enumerate(remaining_songs):
        remaining_song.position = i + 1
    
    db.commit()
    return True
