# -*- coding: utf-8 -*-
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from app.database import Base


class RequerimientooDB(Base):
    __tablename__ = "requerimientos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=False)
    tipo = Column(String(50), nullable=False)
    prioridad = Column(String(20), nullable=False)
    estado = Column(String(30), nullable=False, default="Nuevo")
    autor_id = Column(Integer, nullable=False)
    autor_rol = Column(String(30), nullable=False)
    autor_email = Column(String(100), default="")
    creado_en = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    proyecto_id = Column(Integer, ForeignKey("proyectos.id"), nullable=False)


class CambioEstadoDB(Base):
    __tablename__ = "historial_cambios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    requerimiento_id = Column(Integer, ForeignKey("requerimientos.id"), nullable=False)
    usuario_id = Column(Integer, nullable=False)
    rol_usuario = Column(String(30), nullable=False)
    estado_anterior = Column(String(30), nullable=False)
    estado_nuevo = Column(String(30), nullable=False)
    fecha = Column(DateTime, default=lambda: datetime.now(timezone.utc))
