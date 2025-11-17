import cloudinary
import cloudinary.uploader
import os
from fastapi import UploadFile

# Configurar Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

def upload_playlist_cover(file: UploadFile, playlist_id: str) -> str:
    """
    Sube una imagen a Cloudinary y retorna la URL
    """
    try:
        # Subir imagen a Cloudinary
        result = cloudinary.uploader.upload(
            file.file,
            folder="playlist_covers",  # Organizar en carpeta
            public_id=f"playlist_{playlist_id}",  # Nombre único
            overwrite=True,  # Sobrescribir si existe
            resource_type="image",
            transformation=[
                {"width": 500, "height": 500, "crop": "fill"},  # Redimensionar
                {"quality": "auto"},  # Optimizar calidad
                {"format": "jpg"}  # Convertir a JPG
            ]
        )
        
        return result.get("secure_url")
        
    except Exception as e:
        raise Exception(f"Error al subir imagen: {str(e)}")

def delete_playlist_cover(playlist_id: str):
    """
    Elimina una imagen de Cloudinary
    """
    try:
        cloudinary.uploader.destroy(f"playlist_covers/playlist_{playlist_id}")
    except Exception:
        pass  # No fallar si no existe