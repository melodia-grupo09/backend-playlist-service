from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from uuid import UUID
from app import schemas, database
from app.repositories import playlist_repository as repo

router = APIRouter(prefix="/playlists", tags=["Playlists"])

# Crear playlist (recibe user_id en el body)
@router.post("/", response_model=schemas.Playlist)
def create_playlist(
    playlist: schemas.PlaylistCreate,
    user_id: str,  # viene en el request
    db: Session = Depends(database.get_db)
):
    return repo.create_playlist(db, playlist, user_id)

# Listar playlists (opcional filtrar por user_id)
@router.get("/", response_model=list[schemas.PlaylistWithoutSongs])
def list_playlists(user_id: str | None = None, db: Session = Depends(database.get_db)):
    return repo.get_playlists(db, user_id)

# Obtener detalle de playlist
@router.get("/{playlist_id}", response_model=schemas.Playlist)
def get_playlist(playlist_id: UUID, db: Session = Depends(database.get_db)):
    playlist = repo.get_playlist(db, playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist no encontrada")
    return playlist

# Añadir canción
@router.post("/{playlist_id}/songs", response_model=schemas.PlaylistSong)
def add_song(playlist_id: UUID, song: schemas.PlaylistSongCreate, db: Session = Depends(database.get_db)):
    playlist = repo.get_playlist(db, playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    return repo.add_song(db, playlist_id, song)

# Eliminar canción
@router.delete("/{playlist_id}/songs/{song_id}", status_code=204)
def remove_song(playlist_id: UUID, song_id: UUID, db: Session = Depends(database.get_db)):
    success = repo.remove_song(db, playlist_id, song_id)
    if not success:
        raise HTTPException(status_code=404, detail="Canción no encontrada en la playlist")
    return {}

@router.delete("/{playlist_id}", status_code=204)
def delete_playlist(
    playlist_id: UUID,
    user_id: str = Header(..., description="ID del usuario"),
    db: Session = Depends(database.get_db)
):
    """Elimina una playlist y todas sus canciones asociadas"""
    success = repo.delete_playlist(db, playlist_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Playlist no encontrada o no tienes permiso para eliminarla")
    return {}

