import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.deps import get_current_user, get_db
from app.db import Base
from app.main import app
from app.models import Profile

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@pytest.fixture()
def db():
    Base.metadata.create_all(engine)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture()
def user(db):
    profile = Profile(id=uuid.uuid4(), display_name="Test User")
    db.add(profile)
    db.commit()
    return profile


@pytest.fixture()
def other_user(db):
    profile = Profile(id=uuid.uuid4(), display_name="Other User")
    db.add(profile)
    db.commit()
    return profile


@pytest.fixture()
def client(db, user):
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_user] = lambda: user
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


@pytest.fixture()
def as_other_user(db, other_user):
    """Swap the authed user mid-test to check ownership isolation."""

    def _swap():
        app.dependency_overrides[get_current_user] = lambda: other_user

    return _swap
