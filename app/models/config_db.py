# -*- coding: utf-8 -*-
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text

from app.database import Base


class ProyectoConfigCampoDB(Base):
    __tablename__ = "proyecto_config_campos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    proyecto_id = Column(Integer, ForeignKey("proyectos.id"), nullable=False)
    nombre = Column(String(100), nullable=False)
    clave = Column(String(50), nullable=False)
    tipo = Column(String(20), nullable=False)
    opciones = Column(Text, nullable=True)
    obligatorio = Column(Boolean, default=False)
    orden = Column(Integer, default=0)


class ProyectoConfigEstadoDB(Base):
    __tablename__ = "proyecto_config_estados"

    id = Column(Integer, primary_key=True, autoincrement=True)
    proyecto_id = Column(Integer, ForeignKey("proyectos.id"), nullable=False)
    nombre = Column(String(100), nullable=False)
    color = Column(String(7), nullable=False)
    orden = Column(Integer, default=0)
    es_terminal = Column(Boolean, default=False)


class RequerimientoValorCampoDB(Base):
    __tablename__ = "requerimiento_valor_campo"

    id = Column(Integer, primary_key=True, autoincrement=True)
    requerimiento_id = Column(Integer, ForeignKey("requerimientos.id"), nullable=False)
    campo_id = Column(Integer, ForeignKey("proyecto_config_campos.id"), nullable=False)
    valor = Column(Text, nullable=True)
