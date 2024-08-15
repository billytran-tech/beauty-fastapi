import pytest
import requests
from httpx import ASGITransport, AsyncClient
from typing import Dict, Generator
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from app.config.database.database import connect_to_database, get_db
from tests.setup.config_tests import env, generate_access_token

from app.main import app

#  Create a test database client
import certifi
ca = certifi.where()


@pytest.fixture(scope="module")
def test_database():
    client = AsyncIOMotorClient(
        env.test_db_url, tlsCAFile=ca, server_api=ServerApi('1'))
    db = client[env.test_db_name]
    yield db
    client.close()


@pytest.fixture(scope="module")
def override_get_db(test_database):
    def _override_get_db():
        return test_database
    return _override_get_db


@pytest.fixture(scope="module")
def test_app(override_get_db):
    app.dependency_overrides[get_db] = override_get_db
    yield app
    app.dependency_overrides.clear()


@pytest.fixture(scope="module")
async def client(test_app):
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="module")
def get_token():
    return generate_access_token()


@pytest.fixture(scope="function")
async def clean_profile_state(client: AsyncClient, get_token: str):
    # Ensure no test profile exists before each test
    headers = {'Authorization': f'Bearer {get_token}'}
    await client.delete(url='/api/customer/delete', headers=headers)
    yield
    # Clean up after test
    await client.delete(url='/api/customer/delete', headers=headers)


@pytest.mark.anyio
async def test_get_non_existent_customer(client: AsyncClient, get_token: str, clean_profile_state):

    headers = {'Authorization': f'Bearer {get_token}'}
    response = await client.get(url="/api/customer/get-my-profile", headers=headers)

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Customer profile does not exist. Please create one."}


@pytest.mark.anyio
async def test_create_customer(client: AsyncClient, get_token: str, clean_profile_state):

    headers = {'Authorization': f'Bearer {get_token}'}
    # client.delete(url='/api/customer/delete', headers=headers)
    response = await client.post(url="/api/customer/create", headers=headers, json={
        "name": "Test User",
        "country": "South Africa"
    })

    assert response.status_code == 201
    assert response.json() == {
        "name": "Test User",
        "country": "South Africa",
        "profile_image_url": None,
        "wishlists": None,
        "settings": {
            "notification_preferences": {
                "BookingChanges": {
                    "sms": True,
                    "email": True,
                    "whatsapp": False
                },
                "BookingReminders": {
                    "sms": True,
                    "email": True,
                    "whatsapp": False
                },
                "SuavUpdates": {
                    "sms": False,
                    "email": True,
                    "whatsapp": False
                },
                "SecuritySettings": {
                    "sms": True,
                    "email": True,
                    "whatsapp": False
                }
            }
        }
    }


@pytest.mark.anyio
async def test_get_existing_profile(client: AsyncClient, get_token: str, clean_profile_state):
    # Setup
    headers = {'Authorization': f'Bearer {get_token}'}
    setup_response = await client.post(url="/api/customer/create", headers=headers, json={
        "name": "Test User",
        "country": "South Africa"
    })
    assert setup_response.status_code == 201

    # Test
    response = await client.get(url="/api/customer/get-my-profile", headers=headers)

    assert response.status_code == 200
    assert response.json() == {
        "name": "Test User",
        "country": "South Africa",
        "profile_image_url": None,
        "wishlists": None,
        "settings": {
            "notification_preferences": {
                "BookingChanges": {
                    "sms": True,
                    "email": True,
                    "whatsapp": False
                },
                "BookingReminders": {
                    "sms": True,
                    "email": True,
                    "whatsapp": False
                },
                "SuavUpdates": {
                    "sms": False,
                    "email": True,
                    "whatsapp": False
                },
                "SecuritySettings": {
                    "sms": True,
                    "email": True,
                    "whatsapp": False
                }
            }
        }
    }


@pytest.mark.anyio
async def test_only_one_customer_account_allowed(client: AsyncClient, get_token: str):
    # Setup
    headers = {'Authorization': f'Bearer {get_token}'}
    setup_response = await client.post(url="/api/customer/create", headers=headers, json={
        "name": "Test User",
        "country": "South Africa"
    })
    assert setup_response.status_code == 201

    # Test
    response = await client.post(url="/api/customer/create", headers=headers, json={"name": "Test User",
                                                                                    "country": "South Africa"
                                                                                    })

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Customer profile already exists. Try to update instead."}


@pytest.mark.anyio
async def test_update_customer_profile(client: AsyncClient, get_token: str, clean_profile_state):
    # Setup
    headers = {'Authorization': f'Bearer {get_token}'}
    setup_response = await client.post(url="/api/customer/create", headers=headers, json={
        "name": "Test User",
        "country": "South Africa"
    })
    assert setup_response.status_code == 201

    # Test
    response = await client.put(url="/api/customer/update/customer-profile", headers=headers, json={
        "name": "Suav Agent",
        "country": "Canada"
    })
    assert response.status_code == 200
    assert response.json() == {
        "name": "Suav Agent",
        "country": "Canada",
        "profile_image_url": None,
        "wishlists": None,
        "settings": {
            "notification_preferences": {
                "BookingChanges": {
                    "sms": True,
                    "email": True,
                    "whatsapp": False
                },
                "BookingReminders": {
                    "sms": True,
                    "email": True,
                    "whatsapp": False
                },
                "SuavUpdates": {
                    "sms": False,
                    "email": True,
                    "whatsapp": False
                },
                "SecuritySettings": {
                    "sms": True,
                    "email": True,
                    "whatsapp": False
                }
            }
        }
    }


@pytest.mark.anyio
async def test_update_customer_profile_with_no_new_data(client: AsyncClient, get_token: str, clean_profile_state):
    # Setup
    headers = {'Authorization': f'Bearer {get_token}'}
    setup_response = await client.post(url="/api/customer/create", headers=headers, json={
        "name": "Test User",
        "country": "South Africa"
    })
    assert setup_response.status_code == 201

    # Test
    response = await client.put(url="/api/customer/update/customer-profile", headers=headers, json={
        "name": "Test User",
        "country": "South Africa"
    })
    assert response.status_code == 304


@pytest.mark.anyio
async def test_update_non_existent_customer_profile(client: AsyncClient, get_token: str, clean_profile_state):
    # Setup
    headers = {'Authorization': f'Bearer {get_token}'}

    # Test
    response = await client.put(url="/api/customer/update/customer-profile", headers=headers, json={
        "name": "Test User",
        "country": "South Africa"
    })
    assert response.status_code == 404


@pytest.mark.anyio
async def test_delete_customer_profile(client: AsyncClient, get_token: str, clean_profile_state):
    headers = {'Authorization': f'Bearer {get_token}'}
    # Setup
    setup_response = await client.post(url="/api/customer/create", headers=headers, json={
        "name": "Test User",
        "country": "South Africa"
    })
    assert setup_response.status_code == 201

    # Test
    response = await client.delete(url="/api/customer/delete", headers=headers)
    assert response.status_code == 200
    assert response.json() == {
        "detail": "Customer profile deleted successfully."}


@pytest.mark.anyio
async def test_delete_non_existent_customer_profile(client: AsyncClient, get_token: str, clean_profile_state):
    # Setup
    headers = {'Authorization': f'Bearer {get_token}'}

    # Test
    response = await client.delete(url="/api/customer/delete", headers=headers)
    assert response.status_code == 404
