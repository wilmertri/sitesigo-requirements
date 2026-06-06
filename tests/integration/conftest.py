# -*- coding: utf-8 -*-
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.requirement_service import RequirementService


@pytest.fixture
def client():
    RequirementService._store.clear()
    RequirementService._next_id = 1
    return TestClient(app)
