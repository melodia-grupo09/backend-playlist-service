import pytest
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

# 1. Configurar SQLite en Memoria PRIMERO
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# ==========================================
# 2. LA LOBOTOMÍA (Monkeypatching)
# ==========================================
# Importamos el módulo de base de datos de tu app
from app import database

# Reemplazamos el engine real (Postgres) por el nuestro (SQLite)
# ANTES de que app.main sea importado.
database.engine = test_engine
database.SessionLocal = TestingSessionLocal

# Mockeamos Cloudinary antes de importar servicios
mock_cloudinary_module = MagicMock()
mock_cloudinary_module.uploader.upload.return_value = {"secure_url": "http://fake.com/img.jpg"}
sys.modules["cloudinary"] = mock_cloudinary_module
sys.modules["cloudinary.uploader"] = mock_cloudinary_module.uploader

# AHORA SÍ importamos tu app.main
# Como database.engine ya es SQLite, create_all(bind=engine) funcionará.
from app.main import app
from app.database import Base, get_db

@pytest.fixture(scope="function")
def db_session():
    """Crea tablas en SQLite, entrega sesión, y limpia al final."""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Cliente HTTP que usa la DB SQLite."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass 
            
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()