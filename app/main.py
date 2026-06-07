# -*- coding: utf-8 -*-
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine
from app.models.requirement_db import Base
from app.models.user_db import UsuarioDB  # noqa: F401 — registra tabla usuarios
from app.routers import auth, requirements

# Crear todas las tablas al iniciar
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ReqFlow API",
    description="API para gestion de requerimientos de software",
    version="0.1.0",
    redirect_slashes=False,
)

origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:5174",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(requirements.router)


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}
