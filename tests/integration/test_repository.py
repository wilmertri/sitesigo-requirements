# -*- coding: utf-8 -*-
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.requirement_db import CambioEstadoDB
from app.repositories.requirement_repository import RequirementRepository
from app.schemas.requirement_schema import Prioridad, RequirementCreate, TipoRequerimiento

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


_DATOS_VALIDOS = RequirementCreate(
    titulo="Sistema de login",
    descripcion="Autenticacion con JWT",
    tipo=TipoRequerimiento.nueva_funcionalidad,
    prioridad=Prioridad.alta,
)


def test_crear_requerimiento_persiste_en_db(db):
    req = RequirementRepository.crear(
        db, _DATOS_VALIDOS, autor_id=1, autor_rol="funcionario", autor_email="a@b.com"
    )

    recuperado = RequirementRepository.obtener_por_id(db, req.id)

    assert recuperado is not None
    assert recuperado.titulo == "Sistema de login"
    assert recuperado.descripcion == "Autenticacion con JWT"
    assert recuperado.tipo == "Nueva funcionalidad"
    assert recuperado.prioridad == "Alta"
    assert recuperado.autor_id == 1
    assert recuperado.autor_email == "a@b.com"
    assert recuperado.estado == "nuevo"


def test_listar_sin_filtros_devuelve_todos(db):
    for i in range(3):
        datos = RequirementCreate(
            titulo=f"Req {i}",
            descripcion=f"Descripcion {i}",
            tipo=TipoRequerimiento.bug,
            prioridad=Prioridad.media,
        )
        RequirementRepository.crear(db, datos, autor_id=1, autor_rol="funcionario")

    lista = RequirementRepository.listar(db)

    assert len(lista) == 3


def test_listar_filtrado_por_estado(db):
    for i in range(2):
        datos = RequirementCreate(
            titulo=f"Nuevo {i}",
            descripcion=f"Desc {i}",
            tipo=TipoRequerimiento.bug,
            prioridad=Prioridad.alta,
        )
        RequirementRepository.crear(db, datos, autor_id=1, autor_rol="funcionario")

    datos_analisis = RequirementCreate(
        titulo="En analisis",
        descripcion="Desc analisis",
        tipo=TipoRequerimiento.bug,
        prioridad=Prioridad.alta,
    )
    req_analisis = RequirementRepository.crear(
        db, datos_analisis, autor_id=1, autor_rol="administrador"
    )
    RequirementRepository.actualizar_estado(db, req_analisis, "en_analisis")

    nuevos = RequirementRepository.listar(db, estado="nuevo")

    assert len(nuevos) == 2


def test_guardar_cambio_estado_crea_historial(db):
    req = RequirementRepository.crear(
        db, _DATOS_VALIDOS, autor_id=1, autor_rol="administrador"
    )

    RequirementRepository.guardar_cambio_estado(
        db,
        requerimiento_id=req.id,
        usuario_id=99,
        rol_usuario="administrador",
        estado_anterior="nuevo",
        estado_nuevo="en_analisis",
    )

    historial = (
        db.query(CambioEstadoDB)
        .filter(CambioEstadoDB.requerimiento_id == req.id)
        .all()
    )

    assert len(historial) == 1
    assert historial[0].estado_anterior == "nuevo"
    assert historial[0].estado_nuevo == "en_analisis"
    assert historial[0].usuario_id == 99
    assert historial[0].rol_usuario == "administrador"
