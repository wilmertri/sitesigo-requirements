# -*- coding: utf-8 -*-
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import requirement_db, user_db, project_db, config_db  # noqa: F401
from app.repositories.config_repository import ConfigRepository
from app.schemas.config_schemas import CampoConfigCreate, EstadoConfigCreate

SQLALCHEMY_TEST_URL = "sqlite://"


@pytest.fixture
def db():
    engine = create_engine(SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSession()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def proyecto_id(db) -> int:
    from app.auth.password_handler import hashear_password
    from app.models.user_db import UsuarioDB
    from app.models.project_db import ProyectoDB

    usuario = UsuarioDB(
        email="owner@test.com",
        hashed_password=hashear_password("pass"),
        rol="super_admin",
        nombre="Owner",
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    proyecto = ProyectoDB(nombre="SITESIGO", creado_por_id=usuario.id)
    db.add(proyecto)
    db.commit()
    db.refresh(proyecto)
    return proyecto.id


@pytest.fixture
def requerimiento_id(db, proyecto_id) -> int:
    from app.models.requirement_db import RequerimientooDB

    req = RequerimientooDB(
        titulo="Req test",
        descripcion="Descripcion test",
        tipo="Bug",
        prioridad="Alta",
        estado="Nuevo",
        autor_id=1,
        autor_rol="funcionario",
        proyecto_id=proyecto_id,
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return req.id


# --- campos ---

def test_crear_campo_persiste_en_db(db, proyecto_id):
    datos = CampoConfigCreate(nombre="Observaciones", clave="observaciones", tipo="texto")
    campo = ConfigRepository.crear_campo(db, proyecto_id, datos)

    assert campo.id is not None
    assert campo.nombre == "Observaciones"
    assert campo.clave == "observaciones"
    assert campo.tipo == "texto"
    assert campo.proyecto_id == proyecto_id


def test_listar_campos_devuelve_los_del_proyecto(db, proyecto_id):
    for nombre, clave in [("Observaciones", "obs"), ("Proceso", "proceso")]:
        ConfigRepository.crear_campo(
            db, proyecto_id,
            CampoConfigCreate(nombre=nombre, clave=clave, tipo="texto"),
        )

    campos = ConfigRepository.listar_campos(db, proyecto_id)

    assert len(campos) == 2


def test_listar_campos_no_mezcla_proyectos(db, proyecto_id):
    from app.models.project_db import ProyectoDB

    otro = ProyectoDB(nombre="Otro Proyecto", creado_por_id=1)
    db.add(otro)
    db.commit()
    db.refresh(otro)

    ConfigRepository.crear_campo(
        db, proyecto_id, CampoConfigCreate(nombre="Campo A", clave="campo_a", tipo="texto")
    )
    ConfigRepository.crear_campo(
        db, otro.id, CampoConfigCreate(nombre="Campo B", clave="campo_b", tipo="texto")
    )

    campos = ConfigRepository.listar_campos(db, proyecto_id)

    assert len(campos) == 1
    assert campos[0].nombre == "Campo A"


def test_crear_campo_lista_guarda_opciones(db, proyecto_id):
    datos = CampoConfigCreate(
        nombre="Proceso",
        clave="proceso",
        tipo="lista",
        opciones=["Seguimiento Fisico", "Informes"],
    )
    campo = ConfigRepository.crear_campo(db, proyecto_id, datos)

    assert campo.opciones is not None
    assert "Seguimiento Fisico" in campo.opciones


# --- estados ---

def test_crear_estado_persiste_en_db(db, proyecto_id):
    datos = EstadoConfigCreate(nombre="En Espera", color="#94a3b8")
    estado = ConfigRepository.crear_estado(db, proyecto_id, datos)

    assert estado.id is not None
    assert estado.nombre == "En Espera"
    assert estado.color == "#94a3b8"
    assert estado.es_terminal is False
    assert estado.proyecto_id == proyecto_id


def test_crear_estado_terminal(db, proyecto_id):
    datos = EstadoConfigCreate(nombre="Entregado", color="#10b981", es_terminal=True)
    estado = ConfigRepository.crear_estado(db, proyecto_id, datos)

    assert estado.es_terminal is True


def test_listar_estados_devuelve_los_del_proyecto(db, proyecto_id):
    for nombre, color in [("En Espera", "#94a3b8"), ("Entregado", "#10b981")]:
        ConfigRepository.crear_estado(
            db, proyecto_id,
            EstadoConfigCreate(nombre=nombre, color=color),
        )

    estados = ConfigRepository.listar_estados(db, proyecto_id)

    assert len(estados) == 2


# --- valores de campo ---

def test_guardar_valor_campo_persiste(db, proyecto_id, requerimiento_id):
    campo = ConfigRepository.crear_campo(
        db, proyecto_id,
        CampoConfigCreate(nombre="Observaciones", clave="obs", tipo="texto"),
    )

    valor = ConfigRepository.guardar_valor_campo(db, requerimiento_id, campo.id, "Texto libre")

    assert valor.id is not None
    assert valor.valor == "Texto libre"
    assert valor.requerimiento_id == requerimiento_id
    assert valor.campo_id == campo.id


def test_listar_valores_campo_del_requerimiento(db, proyecto_id, requerimiento_id):
    campo1 = ConfigRepository.crear_campo(
        db, proyecto_id, CampoConfigCreate(nombre="Obs", clave="obs", tipo="texto")
    )
    campo2 = ConfigRepository.crear_campo(
        db, proyecto_id, CampoConfigCreate(nombre="Proceso", clave="proceso",
                                           tipo="lista", opciones=["Informes"])
    )
    ConfigRepository.guardar_valor_campo(db, requerimiento_id, campo1.id, "Nota")
    ConfigRepository.guardar_valor_campo(db, requerimiento_id, campo2.id, "Informes")

    valores = ConfigRepository.listar_valores_campo(db, requerimiento_id)

    assert len(valores) == 2
