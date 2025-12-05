import pytest
from sqlalchemy.orm import Session
from app.repositories import history_repository
from app.schemas.history import HistoryEntryCreate
from app import models

# --- TEST AGREGAR (Lógica de Pila/Stack) ---

def test_add_history_entry_shifts_positions(db_session: Session):
    user_id = "u1"
    
    # 1. Agregar primera canción
    entry1 = HistoryEntryCreate(song_id="A", song_name="Song A", artist_name="Artist A")
    res1 = history_repository.add_history_entry(db_session, user_id, entry1)
    
    assert res1.position == 1
    
    # 2. Agregar segunda canción (La anterior debe bajar a 2)
    entry2 = HistoryEntryCreate(song_id="B", song_name="Song B", artist_name="Artist B")
    res2 = history_repository.add_history_entry(db_session, user_id, entry2)
    
    assert res2.position == 1 # La nueva es la 1
    
    # Verificar en DB que la vieja ahora es 2
    old_entry = db_session.query(models.HistoryEntry).filter_by(song_id="A").first()
    assert old_entry.position == 2

def test_add_history_multiple_users(db_session: Session):
    """Verificar que no se mezclen los historiales de usuarios distintos"""
    history_repository.add_history_entry(db_session, "u1", HistoryEntryCreate(song_id="A"))
    history_repository.add_history_entry(db_session, "u2", HistoryEntryCreate(song_id="B"))
    
    h1 = history_repository.get_user_history(db_session, "u1")
    h2 = history_repository.get_user_history(db_session, "u2")
    
    assert len(h1) == 1
    assert len(h2) == 1
    assert h1[0].position == 1
    assert h2[0].position == 1

# --- TEST BUSQUEDA Y PAGINACION ---

def test_get_history_paginated_filters(db_session: Session):
    user_id = "u1"
    # Seed data:
    # 1. Rock Song (Artist: Rocker)
    # 2. Pop Song (Artist: Popper)
    # 3. Rock Ballad (Artist: Rocker)
    
    e1 = HistoryEntryCreate(song_id="1", song_name="Rock Song", artist_name="Rocker")
    e2 = HistoryEntryCreate(song_id="2", song_name="Pop Song", artist_name="Popper")
    e3 = HistoryEntryCreate(song_id="3", song_name="Rock Ballad", artist_name="Rocker")
    
    history_repository.add_history_entry(db_session, user_id, e1)
    history_repository.add_history_entry(db_session, user_id, e2)
    history_repository.add_history_entry(db_session, user_id, e3)
    
    # Test Search "Rock" (Debería traer 2: Rock Ballad y Rock Song)
    res_search = history_repository.get_user_history_paginated(db_session, user_id, search="Rock")
    assert res_search["total"] == 2
    
    # Test Artist "Popper"
    res_artist = history_repository.get_user_history_paginated(db_session, user_id, artist="Popper")
    assert res_artist["total"] == 1
    assert res_artist["entries"][0].song_name == "Pop Song"
    
    # Test Pagination (Total 3, limit 2 -> Pag 1 tiene 2, Pag 2 tiene 1)
    res_pag = history_repository.get_user_history_paginated(db_session, user_id, page=1, limit=2)
    assert len(res_pag["entries"]) == 2
    assert res_pag["total_pages"] == 2

# --- TEST BORRAR Y LIMPIAR ---

def test_remove_history_entry_reorder(db_session: Session):
    """
    Estado inicial: [C(1), B(2), A(3)]  <-- C es la más reciente
    Borramos B(2).
    Resultado esperado: [C(1), A(2)]
    """
    user_id = "u1"
    history_repository.add_history_entry(db_session, user_id, HistoryEntryCreate(song_id="A"))
    history_repository.add_history_entry(db_session, user_id, HistoryEntryCreate(song_id="B"))
    history_repository.add_history_entry(db_session, user_id, HistoryEntryCreate(song_id="C"))
    
    # Borrar B
    res = history_repository.remove_history_entry(db_session, user_id, "B")
    assert res is True
    
    # Verificar
    entries = history_repository.get_user_history(db_session, user_id)
    assert len(entries) == 2
    
    # C sigue siendo 1
    assert entries[0].song_id == "C"
    assert entries[0].position == 1
    
    # A subió de 3 a 2
    assert entries[1].song_id == "A"
    assert entries[1].position == 2

def test_remove_non_existent(db_session: Session):
    assert history_repository.remove_history_entry(db_session, "u1", "ghost") is False

def test_clear_history(db_session: Session):
    history_repository.add_history_entry(db_session, "u1", HistoryEntryCreate(song_id="A"))
    
    res = history_repository.clear_history(db_session, "u1")
    assert res is True
    
    entries = history_repository.get_user_history(db_session, "u1")
    assert len(entries) == 0