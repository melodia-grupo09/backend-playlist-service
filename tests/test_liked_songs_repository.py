import pytest
from sqlalchemy.orm import Session
from app.repositories import liked_song_repository
from app.schemas.liked_songs import LikedSongCreate, LikedSongPosition
from app import models

# --- TEST ADD ---

def test_add_liked_song_auto_position(db_session: Session):
    user_id = "u1"
    
    # Agregar primera (pos 1)
    s1 = liked_song_repository.add_liked_song(db_session, user_id, LikedSongCreate(song_id="A"))
    assert s1.position == 1
    
    # Agregar segunda (pos 2)
    s2 = liked_song_repository.add_liked_song(db_session, user_id, LikedSongCreate(song_id="B"))
    assert s2.position == 2

def test_add_liked_song_already_exists(db_session: Session):
    user_id = "u1"
    song = LikedSongCreate(song_id="A")
    
    # Primera vez
    s1 = liked_song_repository.add_liked_song(db_session, user_id, song)
    
    # Segunda vez (debe devolver el existente, no duplicar)
    s2 = liked_song_repository.add_liked_song(db_session, user_id, song)
    
    assert s1.id == s2.id
    # Verificar que solo hay 1 en DB
    count = db_session.query(models.LikedSong).count()
    assert count == 1

# --- TEST REMOVE & REORDER ---

def test_remove_liked_song_reorders(db_session: Session):
    """
    Si tengo [A(1), B(2), C(3)] y borro B(2), C pasa a ser 2.
    """
    user_id = "u1"
    liked_song_repository.add_liked_song(db_session, user_id, LikedSongCreate(song_id="A"))
    liked_song_repository.add_liked_song(db_session, user_id, LikedSongCreate(song_id="B"))
    liked_song_repository.add_liked_song(db_session, user_id, LikedSongCreate(song_id="C"))
    
    # Borrar B
    res = liked_song_repository.remove_liked_song(db_session, user_id, "B")
    assert res is True
    
    # Verificar posiciones
    songs = liked_song_repository.get_user_liked_songs(db_session, user_id)
    
    assert len(songs) == 2
    assert songs[0].song_id == "A"
    assert songs[0].position == 1
    
    assert songs[1].song_id == "C"
    assert songs[1].position == 2 # <-- Reordenado

def test_remove_non_existent(db_session: Session):
    res = liked_song_repository.remove_liked_song(db_session, "u1", "ghost")
    assert res is False

# --- TEST GET ---

def test_get_user_liked_songs(db_session: Session):
    # Usuario 1
    liked_song_repository.add_liked_song(db_session, "u1", LikedSongCreate(song_id="A"))
    # Usuario 2
    liked_song_repository.add_liked_song(db_session, "u2", LikedSongCreate(song_id="B"))
    
    # Fetch u1
    songs_u1 = liked_song_repository.get_user_liked_songs(db_session, "u1")
    assert len(songs_u1) == 1
    assert songs_u1[0].song_id == "A"

# --- TEST IS LIKED ---

def test_is_song_liked_by_user(db_session: Session):
    liked_song_repository.add_liked_song(db_session, "u1", LikedSongCreate(song_id="A"))
    
    assert liked_song_repository.is_song_liked_by_user(db_session, "u1", "A") is True
    assert liked_song_repository.is_song_liked_by_user(db_session, "u1", "B") is False

# --- TEST MANUAL REORDER (update_position y reorder_songs) ---

def test_update_position_move_down(db_session: Session):
    """Mover Pos 1 a Pos 3: [A, B, C] -> [B, C, A]"""
    user_id = "u1"
    liked_song_repository.add_liked_song(db_session, user_id, LikedSongCreate(song_id="A")) # 1
    liked_song_repository.add_liked_song(db_session, user_id, LikedSongCreate(song_id="B")) # 2
    liked_song_repository.add_liked_song(db_session, user_id, LikedSongCreate(song_id="C")) # 3
    
    # Vamos a probar reorder_songs que es más robusto (usa lista)
    updates = [
        LikedSongPosition(song_id="B", position=1),
        LikedSongPosition(song_id="C", position=2),
        LikedSongPosition(song_id="A", position=3)
    ]
    
    res = liked_song_repository.reorder_songs(db_session, user_id, updates)
    assert res is True
    
    songs = liked_song_repository.get_user_liked_songs(db_session, user_id)
    assert songs[0].song_id == "B"
    assert songs[1].song_id == "C"
    assert songs[2].song_id == "A"