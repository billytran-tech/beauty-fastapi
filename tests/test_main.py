import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
    assert response.json() == {
        "msg": "Welcome to Suav Beauty"}, f"Expected response body {{'msg': 'Welcome to Suav Beauty'}}, but got {response.json()}"
