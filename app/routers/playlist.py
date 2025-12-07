from fastapi import APIRouter, Depends, HTTPException, Header, Query, UploadFile, File
from sqlalchemy.orm import Session
from uuid import UUID
from app import schemas, database
from app.repositories import playlist_repository as repo
from app.services.cloudinary_service import upload_playlist_cover, delete_playlist_cover

router = APIRouter(prefix="/playlists", tags=["Playlists"])


# Crear playlist (recibe user_id en el body)
@router.post("/", response_model=schemas.Playlist)
def create_playlist(
    playlist: schemas.PlaylistCreate,
    user_id: str,  # viene en el request
    db: Session = Depends(database.get_db)
):
    return repo.create_playlist(db, playlist, user_id)

# Buscar playlists por nombre con paginación
@router.get("/search")
def search_playlists(
    search: str = Query(None, description="Buscar por nombre de playlist"),
    page: int = Query(1, ge=1, description="Número de página"),
    limit: int = Query(10, ge=1, le=100, description="Playlists por página"),
    user_id: str = Query(None, description="Filtrar por usuario (opcional)"),
    db: Session = Depends(database.get_db)
):
    """Busca playlists por nombre con paginación"""
    result = repo.search_playlists_paginated(db, search, page, limit, user_id)
    
    return {
        "playlists": [
            {
                "id": playlist.id,
                "name": playlist.name,
                "cover_url": playlist.cover_url,
                "owner_id": playlist.owner_id,
                "is_public": playlist.is_public,
                "created_at": playlist.created_at
            }
            for playlist in result["playlists"]
        ],
        "pagination": {
            "page": result["page"],
            "limit": result["limit"],
            "total": result["total"],
            "total_pages": result["total_pages"]
        }
    }

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
def remove_song(playlist_id: UUID, song_id: str, db: Session = Depends(database.get_db)):
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

@router.put("/{playlist_id}/songs/reorder", status_code=200)
def reorder_playlist_songs(
    playlist_id: UUID,
    song_positions: list[schemas.PlaylistSongPositionUpdate],
    db: Session = Depends(database.get_db)
):
    """
    Actualiza las posiciones de canciones en una playlist.
    Solo enviar las canciones que cambiaron de posición.
    """
    success = repo.reorder_playlist_songs(db, playlist_id, song_positions)
    if not success:
        raise HTTPException(
            status_code=404, 
            detail="Error al reordenar canciones o playlist no encontrada"
        )
    return {"message": "Canciones reordenadas correctamente"}

@router.put("/{playlist_id}/cover")
def update_playlist_cover(
    playlist_id: UUID,
    file: UploadFile = File(...),
    user_id: str = Header(..., description="ID del usuario"),
    db: Session = Depends(database.get_db)
):
    """
    Actualiza el cover de una playlist subiendo una imagen a Cloudinary
    """
    # Validar que es una imagen
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")
    
    # Validar tamaño (ej: máximo 5MB)
    if file.size > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="La imagen no puede ser mayor a 5MB")
    
    try:
        # Subir imagen a Cloudinary
        cover_url = upload_playlist_cover(file, str(playlist_id))
        
        # Actualizar en base de datos
        playlist = repo.update_playlist_cover(db, playlist_id, user_id, cover_url)
        
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist no encontrada o no tienes permiso")
        
        return {
            "message": "Cover actualizado exitosamente",
            "cover_url": cover_url,
            "playlist_id": playlist_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar cover: {str(e)}")

@router.patch("/{playlist_id}", response_model=schemas.Playlist)
def update_playlist(
    playlist_id: UUID,
    playlist_update: schemas.PlaylistUpdate,
    user_id: str = Header(..., description="ID del usuario"),
    db: Session = Depends(database.get_db)
):
    """
    Actualiza el nombre y/o visibilidad de una playlist.
    Solo el dueño puede actualizar la playlist.
    """
    playlist = repo.update_playlist(db, playlist_id, user_id, playlist_update)
    
    if not playlist:
        raise HTTPException(
            status_code=404, 
            detail="Playlist no encontrada o no tienes permiso para modificarla"
        )
    
    return playlist



