# -*- coding: utf-8 -*-
"""
Migracion 001 - Agregar soporte multi-tenant.

Agrega proyecto_id a requerimientos y crea las tablas
proyectos y usuario_proyectos si no existen.

Uso:
    DATABASE_URL="postgresql://..." python scripts/migrate_001.py
"""
import os
import sys

import psycopg2


def run():
    database_url = os.getenv("DATABASE_URL", "")
    if not database_url:
        print("ERROR: DATABASE_URL no esta configurada.")
        sys.exit(1)

    # Railway entrega postgres:// en lugar de postgresql://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    print("Conectando a la base de datos...")
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()

    print("Verificando columnas existentes...")

    # Agregar proyecto_id a requerimientos si no existe
    cursor.execute("""
        ALTER TABLE requerimientos
        ADD COLUMN IF NOT EXISTS proyecto_id INTEGER;
    """)
    print("  OK: columna proyecto_id en requerimientos")

    # Crear tabla proyectos si no existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS proyectos (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(100) UNIQUE NOT NULL,
            descripcion TEXT,
            activo BOOLEAN DEFAULT TRUE,
            creado_en TIMESTAMP DEFAULT NOW(),
            creado_por_id INTEGER REFERENCES usuarios(id)
        );
    """)
    print("  OK: tabla proyectos")

    # Crear tabla usuario_proyectos si no existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuario_proyectos (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
            proyecto_id INTEGER NOT NULL REFERENCES proyectos(id),
            rol VARCHAR(30) NOT NULL,
            activo BOOLEAN DEFAULT TRUE,
            creado_en TIMESTAMP DEFAULT NOW(),
            UNIQUE(usuario_id, proyecto_id)
        );
    """)
    print("  OK: tabla usuario_proyectos")

    conn.commit()
    cursor.close()
    conn.close()
    print("Migracion completada exitosamente")


if __name__ == "__main__":
    run()
