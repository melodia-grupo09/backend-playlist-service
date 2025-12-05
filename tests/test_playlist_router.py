import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Asumo que en main.py el prefix es "/playlists" como dice tu router
# Si en main.py haces include_router(..., prefix="/api/playlists"), ajusta esto.
PREFIX = "/playlists"

def test_create_playlist(client):
    """
    POST /playlists/?user_id=...
    """
    payload = {
        "name": "Integration Test",
        "is_public": True,
        "cover_url": "http://default.com"
    }
    
    # user_id es un query param en tu función create_playlist
    response = client.post(f"{PREFIX}/?user_id=user_1", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Integration Test"
    assert data["owner_id"] == "user_1"
    assert "id" in data
    
    return data["id"] # Retornamos el ID para usarlo en otros tests si hiciera falta

def test_get_playlist_detail(client):
    # 1. Crear
    res = client.post(f"{PREFIX}/?user_id=u1", json={"name": "Detail Test"})
    pid = res.json()["id"]
    
    # 2. Obtener
    response = client.get(f"{PREFIX}/{pid}")
    
    assert response.status_code == 200
    assert response.json()["id"] == pid
    assert response.json()["name"] == "Detail Test"

def test_search_playlists(client):
    # Crear playlist para buscar
    client.post(f"{PREFIX}/?user_id=u1", json={"name": "Rock Clasico"})
    
    # Buscar
    response = client.get(f"{PREFIX}/search?search=Rock&page=1&limit=10")
    
    assert response.status_code == 200
    data = response.json()
    assert data["pagination"]["total"] >= 1
    # Verificamos que al menos uno coincida
    assert any(p["name"] == "Rock Clasico" for p in data["playlists"])

def test_add_and_remove_song(client):
    # 1. Crear playlist
    res = client.post(f"{PREFIX}/?user_id=u1", json={"name": "Song List"})
    pid = res.json()["id"]
    
    # 2. Agregar canción
    song_payload = {"song_id": "song_spotify_123"}
    res_add = client.post(f"{PREFIX}/{pid}/songs", json=song_payload)
    
    assert res_add.status_code == 200
    assert res_add.json()["song_id"] == "song_spotify_123"
    assert res_add.json()["position"] == 1
    
    # 3. Eliminar canción
    res_del = client.delete(f"{PREFIX}/{pid}/songs/song_spotify_123")
    assert res_del.status_code == 204

def test_reorder_songs(client):
    # 1. Crear playlist
    res = client.post(f"{PREFIX}/?user_id=u1", json={"name": "Reorder List"})
    pid = res.json()["id"]
    
    # 2. Agregar 2 canciones
    client.post(f"{PREFIX}/{pid}/songs", json={"song_id": "A"})
    client.post(f"{PREFIX}/{pid}/songs", json={"song_id": "B"})
    
    # 3. Reordenar (Invertir posiciones)
    payload = [
        {"song_id": "B", "position": 1},
        {"song_id": "A", "position": 2}
    ]
    res_reorder = client.put(f"{PREFIX}/{pid}/songs/reorder", json=payload)
    
    assert res_reorder.status_code == 200
    assert res_reorder.json()["message"] == "Canciones reordenadas correctamente"

def test_delete_playlist(client):
    # 1. Crear
    res = client.post(f"{PREFIX}/?user_id=u1", json={"name": "To Delete"})
    pid = res.json()["id"]
    
    # 2. Borrar (Requiere Header user-id)
    # Si mandamos mal el header, debería fallar (tu repo chequea owner_id)
    headers = {"user-id": "u1"} 
    res_del = client.delete(f"{PREFIX}/{pid}", headers=headers)
    
    assert res_del.status_code == 204
    
    # 3. Verificar que ya no existe (404)
    res_get = client.get(f"{PREFIX}/{pid}")
    assert res_get.status_code == 404

# --- TEST DE SUBIDA DE ARCHIVOS (Cover) ---

# Mockeamos la función específica que usa tu router
@patch("app.routers.playlist.upload_playlist_cover")
def test_update_playlist_cover_success(mock_upload, client):
    # 1. Configurar Mock de Cloudinary
    mock_upload.return_value = "http://cloudinary.com/new_cover.jpg"
    
    # 2. Crear Playlist
    res = client.post(f"{PREFIX}/?user_id=u1", json={"name": "Cover Test"})
    pid = res.json()["id"]
    
    # 3. Preparar archivo falso (imagen pequeña)
    file_content = b"fake image content"
    files = {"file": ("cover.jpg", file_content, "image/jpeg")}
    
    # 4. Enviar PUT con Header y File
    headers = {"user-id": "u1"}
    response = client.put(f"{PREFIX}/{pid}/cover", headers=headers, files=files)
    
    assert response.status_code == 200
    assert response.json()["cover_url"] == "http://cloudinary.com/new_cover.jpg"
    
    # Verificar que se llamó al servicio de subida
    mock_upload.assert_called_once()

def test_update_playlist_cover_invalid_file(client):
    # Crear Playlist
    res = client.post(f"{PREFIX}/?user_id=u1", json={"name": "Bad File"})
    pid = res.json()["id"]
    
    # Enviar archivo de texto (no imagen)
    files = {"file": ("test.txt", b"texto", "text/plain")}
    headers = {"user-id": "u1"}
    
    response = client.put(f"{PREFIX}/{pid}/cover", headers=headers, files=files)
    
    # Validamos el status
    assert response.status_code == 400
    
    # CORRECCIÓN: Buscamos el texto dentro de la respuesta cruda para evitar KeyError
    # Esto funcionará si la respuesta es {"detail": ...} o {"message": ...}
    assert "imagen" in response.text