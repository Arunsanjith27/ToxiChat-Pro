import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health(client):
    res = await client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["app"] == "ToxiChat Pro"
    assert data["status"] == "running"


@pytest.mark.asyncio
async def test_register_and_login(client):
    reg = await client.post("/api/register", json={
        "username": "testuser",
        "password": "pass1234",
        "display_name": "Test User",
    })
    assert reg.status_code == 200
    reg_data = reg.json()
    assert "access_token" in reg_data
    assert reg_data["username"] == "testuser"

    login = await client.post("/api/login", json={
        "username": "testuser",
        "password": "pass1234",
    })
    assert login.status_code == 200
    assert login.json()["access_token"]


@pytest.mark.asyncio
async def test_protected_route_requires_auth(client):
    res = await client.get("/api/users")
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_predict_toxicity(client):
    reg = await client.post("/api/register", json={
        "username": "toxuser", "password": "pass1234",
    })
    token = reg.json()["access_token"]
    res = await client.post(
        "/api/predict",
        json={"text": "hello friend"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "score" in data
    assert "label" in data


@pytest.mark.asyncio
async def test_forgot_and_reset_password(client):
    await client.post("/api/register", json={
        "username": "resetuser", "password": "oldpass1",
    })
    forgot = await client.post("/api/auth/forgot-password", json={"username": "resetuser"})
    assert forgot.status_code == 200
    token = forgot.json()["token"]
    assert token

    reset = await client.post("/api/auth/reset-password", json={
        "token": token, "new_password": "newpass1",
    })
    assert reset.status_code == 200

    login = await client.post("/api/login", json={
        "username": "resetuser", "password": "newpass1",
    })
    assert login.status_code == 200


@pytest.mark.asyncio
async def test_escalation_prediction(client):
    reg = await client.post("/api/register", json={
        "username": "escuser", "password": "pass1234",
    })
    token = reg.json()["access_token"]
    res = await client.post(
        "/api/predict/escalation",
        json={"text": "you are stupid", "partner": "someone"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "escalation" in data
    assert "conversation_health" in data
