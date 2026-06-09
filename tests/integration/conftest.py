# -*- coding: utf-8 -*-
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth.jwt_handler import crear_token
from app.auth.password_handler import hashear_password
from app.database import Base, get_db
from app.main import app
from app.models.config_db import ProyectoConfigCampoDB, ProyectoConfigEstadoDB, RequerimientoValorCampoDB  # noqa: F401
from app.models.project_db import ProyectoDB, UsuarioProyectoDB  # noqa: F401
from app.models.requirement_db import CambioEstadoDB, RequerimientooDB  # noqa: F401
from app.models.user_db import UsuarioDB  # noqa: F401

SQLALCHEMY_TEST_URL = "sqlite://"


@pytest.fixture
def engine():
    eng = create_engine(
        SQLALCHEMY_TEST_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=eng)
    yield eng
    Base.metadata.drop_all(bind=eng)


@pytest.fixture
def db(engine):
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(engine):
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        session = Session()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def admin_token(client, db) -> str:
    admin = UsuarioDB(
        email="admin@test.com",
        hashed_password=hashear_password("admin123"),
        rol="administrador",
        nombre="Admin Test",
        activo=True,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)

    proyecto = ProyectoDB(
        nombre="Proyecto Test",
        descripcion="",
        activo=True,
        creado_por_id=admin.id,
    )
    db.add(proyecto)
    db.commit()
    db.refresh(proyecto)

    db.add(UsuarioProyectoDB(
        usuario_id=admin.id,
        proyecto_id=proyecto.id,
        rol="administrador",
        activo=True,
    ))
    db.commit()

    return crear_token({
        "sub": str(admin.id),
        "email": admin.email,
        "rol": "administrador",
        "nombre": admin.nombre,
        "proyecto_id": proyecto.id,
    })


@pytest.fixture
def super_admin_token(client, db) -> tuple[str, int]:
    """Devuelve (token, proyecto_id) para un usuario super_admin."""
    sa = UsuarioDB(
        email="superadmin@test.com",
        hashed_password=hashear_password("sa123"),
        rol="super_admin",
        nombre="Super Admin Test",
        activo=True,
    )
    db.add(sa)
    db.commit()
    db.refresh(sa)

    proyecto = ProyectoDB(
        nombre="Proyecto SA Test",
        descripcion="",
        activo=True,
        creado_por_id=sa.id,
    )
    db.add(proyecto)
    db.commit()
    db.refresh(proyecto)

    token = crear_token({
        "sub": str(sa.id),
        "email": sa.email,
        "rol": "super_admin",
        "nombre": sa.nombre,
        "proyecto_id": proyecto.id,
    })
    return token, proyecto.id


@pytest.fixture
def funcionario_token(client, db, admin_token) -> str:
    proyecto = db.query(ProyectoDB).first()

    func = UsuarioDB(
        email="funcionario@test.com",
        hashed_password=hashear_password("func123"),
        rol="funcionario",
        nombre="Funcionario Test",
        activo=True,
    )
    db.add(func)
    db.commit()
    db.refresh(func)

    db.add(UsuarioProyectoDB(
        usuario_id=func.id,
        proyecto_id=proyecto.id,
        rol="funcionario",
        activo=True,
    ))
    db.commit()

    return crear_token({
        "sub": str(func.id),
        "email": func.email,
        "rol": "funcionario",
        "nombre": func.nombre,
        "proyecto_id": proyecto.id,
    })
