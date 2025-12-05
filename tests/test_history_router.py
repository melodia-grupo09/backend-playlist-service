import pytest
from fastapi.testclient import TestClient

# Prefijo definido en tu router
PREFIX = "/history"

def test_add_history_entry(client):
    headers = {"user-id": "u1"}
    
    payload = {
        "song_id": "song_1",
        "song_name": "Bohemian Rhapsody",
        "artist_name": "Queen",
        "minutos": "5:55"
    }
    
    # 1. Agregar entrada (POST)
    response = client.post(f"{PREFIX}/", json=payload, headers=headers)
    
    assert response.status_code == 201
    data = response.json()
    assert data["song_id"] == "song_1"
    assert data["song_name"] == "Bohemian Rhapsody"
    assert data["position"] == 1 # La más reciente es la 1

def test_get_history_pagination_and_search(client):
    headers = {"user-id": "u1"}
    
    # Setup: Agregar 3 canciones
    # A (Artist: Queen), B (Artist: Beatles), C (Artist: Queen)
    client.post(f"{PREFIX}/", json={"song_id": "A", "artist_name": "Queen"}, headers=headers)
    client.post(f"{PREFIX}/", json={"song_id": "B", "artist_name": "Beatles"}, headers=headers)
    client.post(f"{PREFIX}/", json={"song_id": "C", "artist_name": "Queen"}, headers=headers)
    
    # 1. Test Básico (GET All)
    res_all = client.get(f"{PREFIX}/", headers=headers)
    assert res_all.status_code == 200
    assert res_all.json()["pagination"]["total"] == 3
    
    # 2. Test Filtro Artista (Query param)
    res_filter = client.get(f"{PREFIX}/?artist=Beatles", headers=headers)
    assert res_filter.status_code == 200
    history = res_filter.json()["history"]
    assert len(history) == 1
    assert history[0]["song_id"] == "B"

def test_remove_history_entry_success(client):
    headers = {"user-id": "u1"}
    # Crear
    client.post(f"{PREFIX}/", json={"song_id": "song_to_delete"}, headers=headers)
    
    # Borrar
    response = client.delete(f"{PREFIX}/song_to_delete", headers=headers)
    
    assert response.status_code == 204
    
    # Verificar que no está
    res_get = client.get(f"{PREFIX}/", headers=headers)
    # Buscamos si existe alguno con ese ID
    found = any(x["song_id"] == "song_to_delete" for x in res_get.json()["history"])
    assert not found

def test_remove_history_entry_not_found(client):
    headers = {"user-id": "u1"}
    
    response = client.delete(f"{PREFIX}/ghost_song", headers=headers)
    
    assert response.status_code == 404
    # Usamos .text para evitar errores de formato JSON (KeyError 'detail')
    assert "no encontrada" in response.text

def test_clear_history_success(client):
    headers = {"user-id": "u1"}
    # Llenar historial
    client.post(f"{PREFIX}/", json={"song_id": "A"}, headers=headers)
    client.post(f"{PREFIX}/", json={"song_id": "B"}, headers=headers)
    
    # Borrar todo
    response = client.delete(f"{PREFIX}/", headers=headers)
    assert response.status_code == 204
    
    # Verificar vacío
    res_get = client.get(f"{PREFIX}/", headers=headers)
    assert res_get.json()["pagination"]["total"] == 0

def test_clear_history_empty_fails(client):
    """Tu router devuelve 404 si intentas borrar un historial que ya está vacío"""
    headers = {"user-id": "new_user_empty"}
    
    response = client.delete(f"{PREFIX}/", headers=headers)
    
    assert response.status_code == 404
    assert "No se encontró historial" in response.text