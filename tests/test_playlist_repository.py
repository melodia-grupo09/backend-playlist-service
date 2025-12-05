import pytest
from sqlalchemy.orm import Session
from app.repositories import playlist_repository
from app import models
# Importamos tus schemas reales
from app.schemas.playlist import PlaylistCreate
from app.schemas.playlist_songs import PlaylistSongCreate, PlaylistSongPositionUpdate

# --- TEST DE CREACIÓN Y LECTURA ---

def test_create_playlist(db_session: Session):
    # Usamos tu schema real
    playlist_data = PlaylistCreate(name="My Mix", is_public=True)
    user_id = "user_1"
    
    playlist = playlist_repository.create_playlist(db_session, playlist_data, user_id)
    
    assert playlist.id is not None
    assert playlist.name == "My Mix"
    assert playlist.owner_id == user_id
    assert playlist.is_public is True

def test_get_playlists_filter(db_session: Session):
    # Creamos datos
    p1_data = PlaylistCreate(name="P1")
    p2_data = PlaylistCreate(name="P2")
    
    playlist_repository.create_playlist(db_session, p1_data, "u1")
    playlist_repository.create_playlist(db_session, p2_data, "u2")
    
    # Test filtro por usuario
    user_p = playlist_repository.get_playlists(db_session, user_id="u1")
    assert len(user_p) == 1
    assert user_p[0].name == "P1"

def test_update_cover(db_session: Session):
    p = playlist_repository.create_playlist(db_session, PlaylistCreate(name="P1"), "u1")
    
    # Intento actualizar con usuario incorrecto (u2)
    res = playlist_repository.update_playlist_cover(db_session, p.id, "u2", "http://new")
    assert res is None
    
    # Usuario correcto (u1)
    res = playlist_repository.update_playlist_cover(db_session, p.id, "u1", "http://new")
    assert res.cover_url == "http://new"

def test_delete_playlist(db_session: Session):
    p = playlist_repository.create_playlist(db_session, PlaylistCreate(name="Delete Me"), "u1")
    
    # Agregar canción para verificar borrado en cascada
    song_data = PlaylistSongCreate(song_id="s1")
    playlist_repository.add_song(db_session, p.id, song_data)
    
    # Borrar
    result = playlist_repository.delete_playlist(db_session, p.id, "u1")
    assert result is True
    
    # Verificar que ya no existe
    found = playlist_repository.get_playlist(db_session, p.id)
    assert found is None

# --- TESTS DE CANCIONES (Lógica compleja) ---

def test_add_song_auto_position(db_session: Session):
    p = playlist_repository.create_playlist(db_session, PlaylistCreate(name="Songs"), "u1")
    
    # Usamos tu schema PlaylistSongCreate
    s1 = playlist_repository.add_song(db_session, p.id, PlaylistSongCreate(song_id="song_A"))
    s2 = playlist_repository.add_song(db_session, p.id, PlaylistSongCreate(song_id="song_B"))
    
    assert s1.position == 1
    assert s2.position == 2

def test_remove_song_reorders_remaining(db_session: Session):
    """
    Si borramos la del medio (2), la 3 pasa a ser la 2.
    """
    p = playlist_repository.create_playlist(db_session, PlaylistCreate(name="Order"), "u1")
    
    playlist_repository.add_song(db_session, p.id, PlaylistSongCreate(song_id="A")) # Pos 1
    playlist_repository.add_song(db_session, p.id, PlaylistSongCreate(song_id="B")) # Pos 2
    playlist_repository.add_song(db_session, p.id, PlaylistSongCreate(song_id="C")) # Pos 3
    
    # Borramos canción B
    playlist_repository.remove_song(db_session, p.id, "B")
    
    songs = db_session.query(models.PlaylistSong).filter_by(playlist_id=p.id).order_by(models.PlaylistSong.position).all()
    
    assert len(songs) == 2
    assert songs[0].song_id == "A"
    assert songs[0].position == 1
    
    assert songs[1].song_id == "C"
    assert songs[1].position == 2 # <-- Reordenado

def test_reorder_move_down(db_session: Session):
    """Mover Pos 1 a Pos 3: [A, B, C] -> [B, C, A]"""
    p = playlist_repository.create_playlist(db_session, PlaylistCreate(name="Reorder"), "u1")
    
    playlist_repository.add_song(db_session, p.id, PlaylistSongCreate(song_id="A"))
    playlist_repository.add_song(db_session, p.id, PlaylistSongCreate(song_id="B"))
    playlist_repository.add_song(db_session, p.id, PlaylistSongCreate(song_id="C"))
    
    # Usamos tu schema PlaylistSongPositionUpdate
    updates = [PlaylistSongPositionUpdate(song_id="A", position=3)]
    
    playlist_repository.reorder_playlist_songs(db_session, p.id, updates)
    
    songs = db_session.query(models.PlaylistSong).filter_by(playlist_id=p.id).order_by(models.PlaylistSong.position).all()
    
    assert songs[0].song_id == "B"
    assert songs[1].song_id == "C"
    assert songs[2].song_id == "A"

# --- TESTS: BÚSQUEDA ---

def test_search_paginated(db_session: Session):
    # Creamos 5 playlists que digan "Rock"
    for i in range(5):
        playlist_repository.create_playlist(db_session, PlaylistCreate(name=f"Rock {i}"), "u1")
    
    # Creamos 1 que diga "Pop"
    playlist_repository.create_playlist(db_session, PlaylistCreate(name="Pop Music"), "u1")
    
    # Buscar "Rock"
    result = playlist_repository.search_playlists_paginated(db_session, search="Rock", page=1, limit=10)
    
    assert result["total"] == 5
    assert len(result["playlists"]) == 5
    
    # Buscar "Pop"
    result_pop = playlist_repository.search_playlists_paginated(db_session, search="Pop")
    assert result_pop["total"] == 1