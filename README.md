# backend-playlist-service

Microservicios auxiliares para el backend de Melodia, desarrollados con FastAPI.

---

## 📚 Índice

- [Introducción](#introducción)
- [Requisitos](#requisitos)
- [Ejecución](#ejecución)

---

## Introducción

Este repositorio aloja el backend encargado de la gestión de Playlists, Canciones Favoritas (Likes) e Historial de Reproducción. Está construido con FastAPI y SQLAlchemy, implementando una Clean Architecture por capas para mantener el código organizado y escalable.

El proyecto sigue una estructura de Capas (Layered Architecture), separando claramente las responsabilidades:

---

## Requisitos

- Docker
- Docker Compose
- Configurar el archivo .env con los datos de postgres y el servicio de cloudinary

---

## Ejecución

1. Cloná el repositorio:

   ```bash
   git clone https://github.com/tu-org/melodia-microservices.git
   cd melodia-microservices
   ```

2. Copiá el archivo de entorno:

   ```bash
   cp .env.example .env
   ```

3. Levantá el microservicio:

   ```bash
   docker-compose up --build
   ```

4. Ejecutar los tests

   ```bash
   # Correr todos los tests
   docker compose -f docker-compose.test.yml up --build
   ```