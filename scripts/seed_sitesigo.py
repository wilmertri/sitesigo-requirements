# -*- coding: utf-8 -*-
"""
Seed inicial para el proyecto SITESIGO.

Configura los 6 campos adicionales del proyecto.
Los estados se gestionan con el enum base de ReqFlow
(Nuevo, En analisis, En desarrollo, Resuelto, Cerrado, Rechazado).

Uso:
    python scripts/seed_sitesigo.py
    python scripts/seed_sitesigo.py --proyecto-id 2
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import config_db, project_db, requirement_db, user_db  # noqa: F401
from app.models.config_db import ProyectoConfigCampoDB
from app.models.project_db import ProyectoDB

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sitesigo.db").replace(
    "postgres://", "postgresql://", 1
)

CAMPOS_SITESIGO = [
    {
        "nombre": "Observaciones",
        "clave": "observaciones",
        "tipo": "texto",
        "opciones": None,
        "obligatorio": False,
        "orden": 1,
    },
    {
        "nombre": "Proceso",
        "clave": "proceso",
        "tipo": "lista",
        "opciones": json.dumps([
            "Seguimiento Fisico",
            "Seguimiento Financiero",
            "Banco de Proyectos",
            "Politica Publica",
            "Informes",
            "Todos",
        ]),
        "obligatorio": False,
        "orden": 2,
    },
    {
        "nombre": "Fecha Inicio",
        "clave": "fecha_inicio",
        "tipo": "fecha",
        "opciones": None,
        "obligatorio": False,
        "orden": 3,
    },
    {
        "nombre": "Fecha Final",
        "clave": "fecha_final",
        "tipo": "fecha",
        "opciones": None,
        "obligatorio": False,
        "orden": 4,
    },
    {
        "nombre": "Dias habiles",
        "clave": "dias_habiles",
        "tipo": "calculado",
        "opciones": None,
        "obligatorio": False,
        "orden": 5,
    },
    {
        "nombre": "Obligacion contractual",
        "clave": "obligacion_contractual",
        "tipo": "numero",
        "opciones": None,
        "obligatorio": False,
        "orden": 6,
    },
]


def obtener_proyecto_id(db, nombre: str) -> int:
    proyecto = db.query(ProyectoDB).filter(ProyectoDB.nombre == nombre).first()
    if not proyecto:
        raise SystemExit(f"ERROR: No se encontro el proyecto '{nombre}' en la base de datos.")
    return proyecto.id


def campos_ya_existen(db, proyecto_id: int) -> bool:
    count = db.query(ProyectoConfigCampoDB).filter(
        ProyectoConfigCampoDB.proyecto_id == proyecto_id
    ).count()
    return count > 0


def crear_campos(db, proyecto_id: int) -> None:
    for campo in CAMPOS_SITESIGO:
        db.add(ProyectoConfigCampoDB(
            proyecto_id=proyecto_id,
            nombre=campo["nombre"],
            clave=campo["clave"],
            tipo=campo["tipo"],
            opciones=campo["opciones"],
            obligatorio=campo["obligatorio"],
            orden=campo["orden"],
        ))
    db.commit()


def main():
    parser = argparse.ArgumentParser(description="Seed campos SITESIGO")
    parser.add_argument("--proyecto-id", type=int, default=None,
                        help="ID del proyecto (default: busca por nombre 'SITESIGO')")
    args = parser.parse_args()

    connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
    engine = create_engine(DATABASE_URL, connect_args=connect_args)
    Session = sessionmaker(bind=engine)
    db = Session()

    try:
        proyecto_id = args.proyecto_id or obtener_proyecto_id(db, "SITESIGO")
        print(f"Proyecto ID: {proyecto_id}")

        if campos_ya_existen(db, proyecto_id):
            print("Los campos ya existen. Nada que hacer.")
            return

        crear_campos(db, proyecto_id)
        print(f"Creados {len(CAMPOS_SITESIGO)} campos para el proyecto {proyecto_id}:")
        for c in CAMPOS_SITESIGO:
            print(f"  [{c['orden']}] {c['nombre']} ({c['tipo']})")
    finally:
        db.close()


if __name__ == "__main__":
    main()
