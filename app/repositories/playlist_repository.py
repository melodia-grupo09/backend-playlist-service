from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from uuid import UUID
from app import models, schemas

def create_playlist(db: Session, playlist: schemas.PlaylistCreate, user_id: str):
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
    playlist = get_playlist(db, playlist_id)
    if not playlist:
        return None

    max_position = db.query(func.max(models.PlaylistSong.position)).filter(
        models.PlaylistSong.playlist_id == playlist_id
    ).scalar() or 0
    
    new_song = models.PlaylistSong(
        playlist_id=playlist_id,
        song_id=song.song_id,
        position=max_position + 1
    )
    
    db.add(new_song)
    db.commit()
    db.refresh(new_song)
    return new_song

def remove_song(db: Session, playlist_id: UUID, song_id: str):
    song = db.query(models.PlaylistSong).filter(
        models.PlaylistSong.playlist_id == playlist_id,
        models.PlaylistSong.song_id == song_id
    ).first()
    
    if not song:
        return False
    
    # Guardar posición para reordenar
    deleted_position = song.position
    
    db.delete(song)
    db.commit()
    
    # Reordenar las posiciones de las canciones restantes
    remaining_songs = db.query(models.PlaylistSong).filter(
        models.PlaylistSong.playlist_id == playlist_id,
        models.PlaylistSong.position > deleted_position
    ).all()
    
    for song in remaining_songs:
        song.position -= 1
    
    db.commit()
    return True

def delete_playlist(db: Session, playlist_id: UUID, user_id: str):
    playlist = db.query(models.Playlist).filter(
        models.Playlist.id == playlist_id,
        models.Playlist.owner_id == user_id
    ).first()
    
    if not playlist:
        return False
    db.query(models.PlaylistSong).filter(
        models.PlaylistSong.playlist_id == playlist_id
    ).delete()
    
    db.delete(playlist)
    db.commit()
    return True

def reorder_playlist_songs(db: Session, playlist_id: UUID, song_positions: list[schemas.PlaylistSongPositionUpdate]):
    """
    Reordena canciones en una playlist, desplazando correctamente las demás canciones.
    """
    playlist = db.query(models.Playlist).filter(
        models.Playlist.id == playlist_id
    ).first()
    
    if not playlist:
        return False
    
    try:
        all_songs = db.query(models.PlaylistSong).filter(
            models.PlaylistSong.playlist_id == playlist_id
        ).order_by(models.PlaylistSong.position).all()
        
        if not all_songs:
            return True
        
        songs_by_id = {str(song.song_id): song for song in all_songs}
        
        for update in song_positions:
            if str(update.song_id) not in songs_by_id:
                return False
            
            if update.position < 1 or update.position > len(all_songs):
                return False
        
        for update in song_positions:
            song_to_move = songs_by_id[str(update.song_id)]
            old_position = song_to_move.position
            new_position = update.position
            
            if old_position == new_position:
                continue
                
            if old_position < new_position:

                for song in all_songs:
                    if old_position < song.position <= new_position:
                        song.position -= 1
                        
            else: 
                for song in all_songs:
                    if new_position <= song.position < old_position:
                        song.position += 1
            
            song_to_move.position = new_position
            
            all_songs.sort(key=lambda s: s.position)
        
        db.commit()
        return True
        
    except Exception as e:
        db.rollback()
        print(f"Error al reordenar canciones: {e}")
        return False
