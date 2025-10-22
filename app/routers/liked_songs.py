from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app import schemas, database
from app.repositories import liked_song_repository as repo

router = APIRouter(
    prefix="/liked-songs",
    tags=["Liked Songs"]
)

@router.get("/", response_model=list[schemas.LikedSong])
def get_liked_songs(
    user_id: str = Header(..., description="ID del usuario"),
    db: Session = Depends(database.get_db)
):
    """Obtiene todas las canciones favoritas del usuario"""
    return repo.get_user_liked_songs(db, user_id)

@router.post("/", response_model=schemas.LikedSong, status_code=201)
def add_liked_song(
    song: schemas.LikedSongCreate,
    user_id: str = Header(..., description="ID del usuario"),
    db: Session = Depends(database.get_db)
):
    """Añade una canción a favoritos"""
    return repo.add_liked_song(db, user_id, song)

@router.delete("/{song_id}", status_code=204)
def remove_liked_song(
    song_id: str,
    user_id: str = Header(..., description="ID del usuario"),
    db: Session = Depends(database.get_db)
):
    """Elimina una canción de favoritos"""
    success = repo.remove_liked_song(db, user_id, song_id)
    if not success:
        raise HTTPException(status_code=404, detail="Canción no encontrada en favoritos")
    return {}

# Nuevo endpoint para actualizar posiciones de múltiples canciones
@router.put("/reorder", status_code=200)
def reorder_songs(
    songs: list[schemas.LikedSongPosition],
    user_id: str = Header(..., description="ID del usuario"),
    db: Session = Depends(database.get_db)
):
    """Actualiza las posiciones de múltiples canciones favoritas"""
    success = repo.reorder_songs(db, user_id, songs)
    if not success:
        raise HTTPException(status_code=404, detail="Error al reordenar canciones")
    return {"message": "Canciones reordenadas correctamente"}

@router.get("/is-liked", response_model=bool)
def is_song_liked(
    user_id: str = Header(..., description="ID del usuario"),
    song_id: str = Header(..., description="ID de la canción"),
    db: Session = Depends(database.get_db)
):
    """
    Devuelve True si la canción está en los liked_songs del usuario, False si no.
    """
    return repo.is_song_liked_by_user(db, user_id, song_id)