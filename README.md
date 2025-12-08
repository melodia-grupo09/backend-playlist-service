# backend-playlist-service

Microservicios auxiliares para el backend de Melodia, desarrollados con FastAPI.

<div align="center">

<a href="https://app.codecov.io/gh/melodia-grupo09/backend-playlist-service" target="_blank">
  <img src="https://codecov.io/gh/melodia-grupo09/backend-playlist-service/graph/badge.svg?token=5OVFEV5RV7" alt="Coverage Status" style="height: 28px;" />
</a>

<a href="https://www.python.org/" target="_blank">
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Version" />
</a>

<a href="https://fastapi.tiangolo.com/" target="_blank">
  <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI Version" />
</a>

<a href="https://www.postgresql.org/" target="_blank">
  <img src="https://img.shields.io/badge/PostgreSQL-15-316192?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
</a>

</div>

---

## 📚 Índice

- [Introducción](#introducción)
- [Code Coverage](#code-coverage)
- [Requisitos](#requisitos)
- [Ejecución](#ejecución)

---

## Introducción

Este repositorio aloja el backend encargado de la gestión de Playlists, Canciones Favoritas (Likes) e Historial de Reproducción. Está construido con FastAPI y SQLAlchemy, implementando una Clean Architecture por capas para mantener el código organizado y escalable.

El proyecto sigue una estructura de Capas (Layered Architecture), separando claramente las responsabilidades:

---

## Code Coverage

La calidad del código está asegurada mediante una estrategia de testing híbrida (**SQLite en Memoria** para tests + **PostgreSQL** para producción).

[![Test Coverage](https://codecov.io/gh/melodia-grupo09/backend-playlist-service/graph/badge.svg?token=5OVFEV5RV7)](https://codecov.io/gh/melodia-grupo09/backend-playlist-service)

**[Ver reporte detallado en Codecov](https://app.codecov.io/gh/melodia-grupo09/backend-playlist-service)**

<h3>Gráfico de Cobertura</h3>
<div align="center">
  <a href="https://app.codecov.io/gh/melodia-grupo09/backend-playlist-service" target="_blank">
    <img src="https://codecov.io/gh/melodia-grupo09/backend-playlist-service/graphs/sunburst.svg?token=5OVFEV5RV7" alt="Coverage Sunburst" width="600" />
  </a>
</div>

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