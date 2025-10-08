# app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError

from app.database import Base, engine
from app.routers import playlist

from app.utils.error_handlers import (
    http_exception_handler,
    validation_exception_handler,
)
from app.logger import log

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Melodia Playlist Service API", version="1.0.0")

log.info("API starting up...")

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.include_router(playlist.router) 