# -*- coding: utf-8 -*-
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


def before_all(context):
    context._engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    context._SessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=context._engine
    )

    def override_get_db():
        db = context._SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    context.client = TestClient(app)


def before_scenario(context, scenario):
    Base.metadata.drop_all(bind=context._engine)
    Base.metadata.create_all(bind=context._engine)
    context.response = None
    context.token = None
    context.requerimiento_id = None
    context.proyecto_id = None


def after_all(context):
    app.dependency_overrides.clear()
