# -*- coding: utf-8 -*-
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.project_db import ProyectoDB, UsuarioProyectoDB  # noqa: F401
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


@pytest.fixture
def proyecto_id(db) -> int:
    from app.auth.password_handler import hashear_password
    from app.models.user_db import UsuarioDB

    usuario = UsuarioDB(
        email="owner@test.com",
        hashed_password=hashear_password("pass"),
        rol="administrador",
        nombre="Owner",
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    proyecto = ProyectoDB(nombre="Proyecto Test", creado_por_id=usuario.id)
    db.add(proyecto)
    db.commit()
    db.refresh(proyecto)
    return proyecto.id


_DATOS_VALIDOS = RequirementCreate(
    titulo="Sistema de login",
    descripcion="Autenticacion con JWT",
    tipo=TipoRequerimiento.nueva_funcionalidad,
    prioridad=Prioridad.alta,
)


def test_crear_requerimiento_persiste_en_db(db, proyecto_id):
    req = RequirementRepository.crear(
        db, _DATOS_VALIDOS, autor_id=1, autor_rol="funcionario",
        autor_email="a@b.com", proyecto_id=proyecto_id,
    )

    recuperado = RequirementRepository.obtener_por_id(db, req.id)

    assert recuperado is not None
    assert recuperado.titulo == "Sistema de login"
    assert recuperado.descripcion == "Autenticacion con JWT"
    assert recuperado.tipo == "Nueva funcionalidad"
    assert recuperado.prioridad == "Alta"
    assert recuperado.autor_id == 1
    assert recuperado.autor_email == "a@b.com"
    assert recuperado.estado == "Nuevo"


def test_listar_sin_filtros_devuelve_todos(db, proyecto_id):
    for i in range(3):
        datos = RequirementCreate(
            titulo=f"Req {i}",
            descripcion=f"Descripcion {i}",
            tipo=TipoRequerimiento.bug,
            prioridad=Prioridad.media,
        )
        RequirementRepository.crear(db, datos, autor_id=1, autor_rol="funcionario",
                                    proyecto_id=proyecto_id)

    lista = RequirementRepository.listar(db)

    assert len(lista) == 3


def test_listar_filtrado_por_estado(db, proyecto_id):
    for i in range(2):
        datos = RequirementCreate(
            titulo=f"Nuevo {i}",
            descripcion=f"Desc {i}",
            tipo=TipoRequerimiento.bug,
            prioridad=Prioridad.alta,
        )
        RequirementRepository.crear(db, datos, autor_id=1, autor_rol="funcionario",
                                    proyecto_id=proyecto_id)

    datos_analisis = RequirementCreate(
        titulo="En analisis",
        descripcion="Desc analisis",
        tipo=TipoRequerimiento.bug,
        prioridad=Prioridad.alta,
    )
    req_analisis = RequirementRepository.crear(
        db, datos_analisis, autor_id=1, autor_rol="administrador",
        proyecto_id=proyecto_id,
    )
    RequirementRepository.actualizar_estado(db, req_analisis, "En analisis")

    nuevos = RequirementRepository.listar(db, estado="Nuevo")

    assert len(nuevos) == 2


def test_archivado_no_aparece_en_listado_normal(db, proyecto_id):
    for i in range(2):
        datos = RequirementCreate(
            titulo=f"Activo {i}",
            descripcion=f"Desc {i}",
            tipo=TipoRequerimiento.bug,
            prioridad=Prioridad.media,
        )
        RequirementRepository.crear(db, datos, autor_id=1, autor_rol="funcionario",
                                    proyecto_id=proyecto_id)

    datos_arch = RequirementCreate(
        titulo="Para archivar",
        descripcion="Sera archivado",
        tipo=TipoRequerimiento.bug,
        prioridad=Prioridad.baja,
    )
    req_arch = RequirementRepository.crear(db, datos_arch, autor_id=1,
                                           autor_rol="administrador",
                                           proyecto_id=proyecto_id)
    RequirementRepository.archivar(db, req_arch.id, usuario_id=99, rol_usuario="administrador")

    lista = RequirementRepository.listar(db)

    assert len(lista) == 2


def test_guardar_cambio_estado_crea_historial(db, proyecto_id):
    req = RequirementRepository.crear(
        db, _DATOS_VALIDOS, autor_id=1, autor_rol="administrador",
        proyecto_id=proyecto_id,
    )

    RequirementRepository.guardar_cambio_estado(
        db,
        requerimiento_id=req.id,
        usuario_id=99,
        rol_usuario="administrador",
        estado_anterior="Nuevo",
        estado_nuevo="En analisis",
    )

    historial = (
        db.query(CambioEstadoDB)
        .filter(CambioEstadoDB.requerimiento_id == req.id)
        .all()
    )

    assert len(historial) == 1
    assert historial[0].estado_anterior == "Nuevo"
    assert historial[0].estado_nuevo == "En analisis"
    assert historial[0].usuario_id == 99
    assert historial[0].rol_usuario == "administrador"
