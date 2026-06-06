# -*- coding: utf-8 -*-
from fastapi import FastAPI
from app.routers import requirements
from app.database import engine
from app.models.requirement_db import Base

# Crear tablas al iniciar
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Gestor de Requerimientos SITESIGO",
    description="API para gestionar requerimientos de SITESIGO",
    version="0.1.0",
)

app.include_router(requirements.router)
