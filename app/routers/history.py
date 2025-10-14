from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from uuid import UUID
from app import schemas, database
from app.repositories import history_repository as repo

router = APIRouter(
    prefix="/history",
    tags=["History"]
)

@router.get("/", response_model=list[schemas.HistoryEntry])
def get_history(
    user_id: UUID = Header(..., description="ID del usuario"),
    db: Session = Depends(database.get_db)
):
    """Obtiene el historial de reproducción del usuario"""
    return repo.get_user_history(db, user_id)

@router.post("/", response_model=schemas.HistoryEntry, status_code=201)
def add_to_history(
    entry: schemas.HistoryEntryCreate,
    user_id: UUID = Header(..., description="ID del usuario"),
    db: Session = Depends(database.get_db)
):
    """Añade una entrada al historial de reproducción"""
    return repo.add_history_entry(db, user_id, entry)

@router.delete("/", status_code=204)
def clear_history(
    user_id: UUID = Header(..., description="ID del usuario"),
    db: Session = Depends(database.get_db)
):
    """Borra todo el historial del usuario"""
    success = repo.clear_history(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="No se encontró historial para este usuario")
    return {}

@router.delete("/{song_id}", status_code=204)
def remove_from_history(
    song_id: UUID,
    user_id: UUID = Header(..., description="ID del usuario"),
    db: Session = Depends(database.get_db)
):
    """Elimina una canción específica del historial"""
    success = repo.remove_history_entry(db, user_id, song_id)
    if not success:
        raise HTTPException(status_code=404, detail="Entrada no encontrada en el historial")
    return {}