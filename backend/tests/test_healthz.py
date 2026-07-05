from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_healthz():
    res = client.get("/healthz")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_me_requires_auth():
    res = client.get("/api/v1/auth/me")
    assert res.status_code == 401
