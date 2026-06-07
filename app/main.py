# -*- coding: utf-8 -*-
from fastapi import FastAPI

from app.database import engine
from app.models.requirement_db import Base
from app.models.user_db import UsuarioDB  # noqa: F401 — registra tabla usuarios
from app.routers import auth, requirements

# Crear todas las tablas al iniciar
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Gestor de Requerimientos SITESIGO",
    description="API para gestionar requerimientos de SITESIGO",
    version="0.1.0",
)

app.include_router(auth.router)
app.include_router(requirements.router)
