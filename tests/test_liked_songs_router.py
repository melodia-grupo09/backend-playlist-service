import pytest
from fastapi.testclient import TestClient

PREFIX = "/liked-songs"

def test_add_and_get_liked_songs(client):
    # 1. Headers obligatorios (según tu router)
    headers = {"user-id": "u1"}
    
    # 2. Agregar canción (POST)
    payload = {"song_id": "song_A"}
    res_add = client.post(f"{PREFIX}/", json=payload, headers=headers)
    
    assert res_add.status_code == 201
    assert res_add.json()["song_id"] == "song_A"
    assert res_add.json()["position"] == 1 # Primera canción = pos 1
    
    # 3. Obtener lista (GET)
    res_get = client.get(f"{PREFIX}/", headers=headers)
    
    assert res_get.status_code == 200
    songs = res_get.json()
    assert len(songs) == 1
    assert songs[0]["song_id"] == "song_A"

def test_remove_liked_song(client):
    headers = {"user-id": "u1"}
    
    # Setup: Agregar canción primero
    client.post(f"{PREFIX}/", json={"song_id": "song_B"}, headers=headers)
    
    # 1. Borrar (DELETE /{song_id})
    res_del = client.delete(f"{PREFIX}/song_B", headers=headers)
    assert res_del.status_code == 204
    
    # 2. Verificar que lista esté vacía
    res_get = client.get(f"{PREFIX}/", headers=headers)
    assert len(res_get.json()) == 0

def test_remove_liked_song_not_found(client):
    headers = {"user-id": "u1"}
    # Intentar borrar algo que no existe
    res = client.delete(f"{PREFIX}/ghost_song", headers=headers)
    
    assert res.status_code == 404
    assert "no encontrada" in res.text

def test_is_song_liked(client):
    headers_check_A = {"user-id": "u1", "song-id": "song_A"}
    headers_check_B = {"user-id": "u1", "song-id": "song_B"}
    
    # Agregar solo A
    client.post(f"{PREFIX}/", json={"song_id": "song_A"}, headers={"user-id": "u1"})
    
    # Chequear A (Debe ser True)
    # Nota: Tu endpoint is-liked pide user_id Y song_id en HEADERS
    res_A = client.get(f"{PREFIX}/is-liked", headers=headers_check_A)
    assert res_A.status_code == 200
    assert res_A.json() is True
    
    # Chequear B (Debe ser False)
    res_B = client.get(f"{PREFIX}/is-liked", headers=headers_check_B)
    assert res_B.status_code == 200
    assert res_B.json() is False

def test_reorder_songs(client):
    headers = {"user-id": "u1"}
    
    # Setup: Agregar A y B
    client.post(f"{PREFIX}/", json={"song_id": "A"}, headers=headers) # Pos 1
    client.post(f"{PREFIX}/", json={"song_id": "B"}, headers=headers) # Pos 2
    
    # Reordenar: B va a 1, A va a 2
    payload = [
        {"song_id": "B", "position": 1},
        {"song_id": "A", "position": 2}
    ]
    
    res_reorder = client.put(f"{PREFIX}/reorder", json=payload, headers=headers)
    
    assert res_reorder.status_code == 200
    
    # Verificar el orden nuevo trayendo la lista
    res_list = client.get(f"{PREFIX}/", headers=headers)
    songs = res_list.json()
    
    # Como tu repo usa order_by position:
    assert songs[0]["song_id"] == "B" # Primero B
    assert songs[0]["position"] == 1
    assert songs[1]["song_id"] == "A" # Segundo A
    assert songs[1]["position"] == 2