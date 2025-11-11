from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.orm import Session
from uuid import UUID
from app import schemas, database
from app.repositories import history_repository as repo

router = APIRouter(
    prefix="/history",
    tags=["History"]
)

@router.get("/")
def get_history(
    user_id: str = Header(..., description="ID del usuario"),
    page: int = Query(1, ge=1, description="Número de página"),
    limit: int = Query(10, ge=1, le=100, description="Entradas por página"),
    search: str = Query(None, description="Buscar por nombre de canción"),
    artist: str = Query(None, description="Filtrar por artista"),
    db: Session = Depends(database.get_db)
):
    """Obtiene el historial de reproducción del usuario con paginación, búsqueda y filtros"""
    result = repo.get_user_history_paginated(db, user_id, page, limit, search, artist)
    
    return {
        "history": result["entries"],
        "pagination": {
            "page": result["page"],
            "limit": result["limit"],
            "total": result["total"],
            "total_pages": result["total_pages"]
        }
    }

@router.post("/", response_model=schemas.HistoryEntry, status_code=201)
def add_to_history(
    entry: schemas.HistoryEntryCreate,
    user_id: str = Header(..., description="ID del usuario"),
    db: Session = Depends(database.get_db)
):
    """Añade una entrada al historial de reproducción"""
    return repo.add_history_entry(db, user_id, entry)

@router.delete("/", status_code=204)
def clear_history(
    user_id: str = Header(..., description="ID del usuario"),
    db: Session = Depends(database.get_db)
):
    """Borra todo el historial del usuario"""
    success = repo.clear_history(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="No se encontró historial para este usuario")
    return {}

@router.delete("/{song_id}", status_code=204)
def remove_from_history(
    song_id: str,
    user_id: str = Header(..., description="ID del usuario"),
    db: Session = Depends(database.get_db)
):
    """Elimina una canción específica del historial"""
    success = repo.remove_history_entry(db, user_id, song_id)
    if not success:
        raise HTTPException(status_code=404, detail="Entrada no encontrada en el historial")
    return {}