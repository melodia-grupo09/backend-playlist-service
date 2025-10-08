from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app import schemas, database
from app.repositories import playlist_repository as repo

router = APIRouter(prefix="/playlists", tags=["Playlists"])

# Crear playlist (recibe user_id en el body)
@router.post("/", response_model=schemas.Playlist)
def create_playlist(
    playlist: schemas.PlaylistCreate,
    user_id: UUID,  # viene en el request
    db: Session = Depends(database.get_db)
):
    return repo.create_playlist(db, playlist, user_id)

# Listar playlists (opcional filtrar por user_id)
@router.get("/", response_model=list[schemas.Playlist])
def list_playlists(user_id: UUID | None = None, db: Session = Depends(database.get_db)):
    return repo.get_playlists(db, user_id)

# Obtener detalle de playlist
@router.get("/{playlist_id}", response_model=schemas.Playlist)
def get_playlist(playlist_id: UUID, db: Session = Depends(database.get_db)):
    playlist = repo.get_playlist(db, playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    return playlist

# Añadir canción
@router.post("/{playlist_id}/songs", response_model=schemas.PlaylistSong)
def add_song(playlist_id: UUID, song: schemas.PlaylistSongCreate, db: Session = Depends(database.get_db)):
    playlist = repo.get_playlist(db, playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    return repo.add_song(db, playlist_id, song)

# Eliminar canción
@router.delete("/songs/{song_id}")
def remove_song(song_id: UUID, db: Session = Depends(database.get_db)):
    ok = repo.remove_song(db, song_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Song not found in playlist")
    return {"ok": True}
