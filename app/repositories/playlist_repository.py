from sqlalchemy.orm import Session
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
    new_song = models.PlaylistSong(playlist_id=playlist_id, **song.dict())
    db.add(new_song)
    db.commit()
    db.refresh(new_song)
    return new_song

def remove_song(db: Session, song_id: UUID):
    song = db.query(models.PlaylistSong).filter(models.PlaylistSong.id == song_id).first()
    if song:
        db.delete(song)
        db.commit()
        return True
    return False
