import pytest
import requests
from httpx import ASGITransport, AsyncClient
# from typing import Dict, Generator
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from app.config.database.database import get_db, get_db_client, get_db_name
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
def test_db_client():
    client = AsyncIOMotorClient(
        env.test_db_url, tlsCAFile=ca, server_api=ServerApi('1'))
    yield client
    client.close()


@pytest.fixture(scope="module")
def test_db_name():
    test_database_name = env.test_db_name
    yield test_database_name


@pytest.fixture(scope="module")
def override_get_db(test_database):
    def _override_get_db():
        return test_database
    return _override_get_db


@pytest.fixture(scope="module")
def override_get_db_client(test_db_client):
    def _override_get_db_client():
        return test_db_client
    return _override_get_db_client


@pytest.fixture(scope="module")
def override_get_db_name(test_db_name):
    def _override_get_db_name():
        return test_db_name
    return _override_get_db_name


@pytest.fixture(scope="module")
def test_app(override_get_db, override_get_db_client, override_get_db_name):
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_db_client] = override_get_db_client
    app.dependency_overrides[get_db_name] = override_get_db_name
    yield app
    app.dependency_overrides.clear()
    # app.dependency_overrides.clear()


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
    await client.delete(url='/api/merchant/delete', headers=headers)
    # assert res.status_code == 200
    # assert res.json() == {
    #     "detail": "Merchant profile and associated username deleted successfully."}
    yield
    # Clean up after test
    await client.delete(url='/api/merchant/delete', headers=headers)
    # assert res.status_code == 200
    # assert res.json() == {
    #     "detail": "Merchant profile and associated username deleted successfully."}

# GET OWNER DETAILS

# TEST CREATE SERVICE WITH NO MERCHANT ACCOUNT


@pytest.mark.anyio
async def test_create_service_no_merchant_account(client: AsyncClient, get_token: str, clean_profile_state):
    headers = {'Authorization': f'Bearer {get_token}'}
    payload = {
        "service_name": "Classic Haircut",
        "duration_minutes": 45,
        "out_call": False,
        "description": "A timeless haircut that suits your style and preferences. Our experienced barbers will give you a fresh look.",
        "price": {
            "currency": {
                "code": "CAD",
                "symbol": "CA$",
                "name": "Canadian Dollar"
            },
            "amount": "25.00"
        }
    }
    response = await client.post("/api/services/create", headers=headers, json=payload)
    assert response.status_code == 401
    assert response.json() == {
        "detail": "You do not have a business profile activated yet. You cannot add a service."}


# TEST CREATE SERVICE


@pytest.mark.anyio
async def test_create_service(client: AsyncClient, get_token: str):
    # SETUP
    headers = {'Authorization': f'Bearer {get_token}'}
    setup_response = await client.post(url='/api/merchant/create', headers=headers, json={
        "username": "suavbarber898",
        "name": "Tshiamo's Barbershop",
        "profession": "Barber",
        "location": {
            "coordinates": {
                "longitude": -79.88573989999999,
                "latitude": 43.5111844
            },
            "country": {
                "name": "South Africa",
                "code": "ZA",
                "currency": {
                    "code": "ZAR",
                    "symbol": "R",
                    "name": "South African Rand"
                }
            },
            "city": "Milton",
            "street_address": "123 Main St E, Milton, ON L9T 1N4, Canada"
        },
        "bio": "Discover the art of grooming at BarberShop XYZ in Toronto, Canada. Our skilled barbers deliver precision haircuts, expert shaves, and a relaxing experience. Book today and elevate your style."
    })
    assert setup_response.status_code == 201

    # TEST
    payload = {
        "service_name": "Classic Haircut",
        "duration_minutes": 45,
        "out_call": False,
        "description": "A timeless haircut that suits your style and preferences. Our experienced barbers will give you a fresh look.",
        "price": {
            "currency": {
                "code": "CAD",
                "symbol": "CA$",
                "name": "Canadian Dollar"
            },
            "amount": "25.00"
        }
    }
    response = await client.post("/api/services/create", headers=headers, json=payload)
    json_response = response.json()
    assert response.status_code == 201

    assert '_id' in json_response
    assert isinstance(json_response['_id'], str)
    service_id = json_response['_id']
    assert len(service_id) > 0

    assert response.json() == {
        "_id": service_id,
        "service_name": "Classic Haircut",
        "duration_minutes": 45,
        "out_call": False,
        "description": "A timeless haircut that suits your style and preferences. Our experienced barbers will give you a fresh look.",
        "price": {
            "currency": {
                "code": "CAD",
                "symbol": "CA$",
                "name": "Canadian Dollar"
            },
            "amount": "25.00"
        },
        "images": None
    }
    # CLEAN UP
    c_res = await client.delete(f'/api/services/delete/{service_id}', headers=headers)
    assert c_res.status_code == 200


# TEST GET SERVICE BY ID
@pytest.mark.anyio
async def test_get_service_by_id(client: AsyncClient, get_token: str, clean_profile_state):
    # SETUP
    headers = {'Authorization': f'Bearer {get_token}'}
    setup_response = await client.post(url='/api/merchant/create', headers=headers, json={
        "username": "suavbarber898",
        "name": "Tshiamo's Barbershop",
        "profession": "Barber",
        "location": {
            "coordinates": {
                "longitude": -79.88573989999999,
                "latitude": 43.5111844
            },
            "country": {
                "name": "South Africa",
                "code": "ZA",
                "currency": {
                    "code": "ZAR",
                    "symbol": "R",
                    "name": "South African Rand"
                }
            },
            "city": "Milton",
            "street_address": "123 Main St E, Milton, ON L9T 1N4, Canada"
        },
        "bio": "Discover the art of grooming at BarberShop XYZ in Toronto, Canada. Our skilled barbers deliver precision haircuts, expert shaves, and a relaxing experience. Book today and elevate your style."
    })
    assert setup_response.status_code == 201

    payload = {
        "service_name": "Classic Haircut",
        "duration_minutes": 45,
        "out_call": False,
        "description": "A timeless haircut that suits your style and preferences. Our experienced barbers will give you a fresh look.",
        "price": {
            "currency": {
                "code": "CAD",
                "symbol": "CA$",
                "name": "Canadian Dollar"
            },
            "amount": "25.00"
        }
    }
    setup_service_response = await client.post("/api/services/create", headers=headers, json=payload)
    json_response = setup_service_response.json()
    assert setup_service_response.status_code == 201
    assert '_id' in json_response
    assert isinstance(json_response['_id'], str)
    service_id = json_response['_id']
    assert len(service_id) > 0

    # TEST
    response = await client.get(f"/api/services/get/{service_id}")
    assert response.status_code == 200
    assert response.json() == {
        "_id": service_id,
        "service_name": "Classic Haircut",
        "duration_minutes": 45,
        "out_call": False,
        "description": "A timeless haircut that suits your style and preferences. Our experienced barbers will give you a fresh look.",
        "price": {
            "currency": {
                "code": "CAD",
                "symbol": "CA$",
                "name": "Canadian Dollar"
            },
            "amount": "25.00"
        },
        "images": None,
        'owner': {
            'location': {
                'city': 'Milton',
                'coordinates': {
                    'latitude': 43.5111844,
                    'longitude': -79.88573989999999
                },
                'country': {
                    'code': 'ZA',
                    'currency': {
                        'code': 'ZAR',
                        'name': 'South African Rand',
                        'symbol': 'R'
                    },
                    'name': 'South Africa'
                },
                'street_address': '123 Main St E, Milton, ON L9T 1N4, Canada'
            },
            'name': "Tshiamo's Barbershop",
            'profession': 'Barber',
            'profile_image_url': None,
            'username': 'suavbarber898'
        },
    }
    # CLEAN UP
    c_res = await client.delete(f'/api/services/delete/{service_id}', headers=headers)
    assert c_res.status_code == 200


# TEST UPDATE SERVICE
@pytest.mark.anyio
async def test_update_service(client: AsyncClient, get_token: str, clean_profile_state):
    # SETUP
    headers = {'Authorization': f'Bearer {get_token}'}
    setup_response = await client.post(url='/api/merchant/create', headers=headers, json={
        "username": "suavbarber898",
        "name": "Tshiamo's Barbershop",
        "profession": "Barber",
        "location": {
            "coordinates": {
                "longitude": -79.88573989999999,
                "latitude": 43.5111844
            },
            "country": {
                "name": "South Africa",
                "code": "ZA",
                "currency": {
                    "code": "ZAR",
                    "symbol": "R",
                    "name": "South African Rand"
                }
            },
            "city": "Milton",
            "street_address": "123 Main St E, Milton, ON L9T 1N4, Canada"
        },
        "bio": "Discover the art of grooming at BarberShop XYZ in Toronto, Canada. Our skilled barbers deliver precision haircuts, expert shaves, and a relaxing experience. Book today and elevate your style."
    })
    assert setup_response.status_code == 201

    payload = {
        "service_name": "Classic Haircut",
        "duration_minutes": 45,
        "out_call": False,
        "description": "A timeless haircut that suits your style and preferences. Our experienced barbers will give you a fresh look.",
        "price": {
            "currency": {
                "code": "CAD",
                "symbol": "CA$",
                "name": "Canadian Dollar"
            },
            "amount": "25.00"
        }
    }
    setup_service_response = await client.post("/api/services/create", headers=headers, json=payload)
    json_response = setup_service_response.json()
    assert setup_service_response.status_code == 201
    assert '_id' in json_response
    assert isinstance(json_response['_id'], str)
    service_id = json_response['_id']
    assert len(service_id) > 0

    # TEST
    response = await client.put(f'/api/services/update/{service_id}', headers=headers, json={
        "service_name": "Classic Haircut",
        "duration_minutes": 50,
        "out_call": False,
        "description": "A timeless haircut that suits your style and preferences. Our experienced barbers will give you a fresh look.",
        "price": {
            "currency": {
                "code": "CAD",
                "symbol": "CA$",
                "name": "Canadian Dollar"
            },
            "amount": "35.00"
        }
    })
    assert response.status_code == 200
    assert response.json() == {
        "_id": service_id,
        "service_name": "Classic Haircut",
        "duration_minutes": 50,
        "out_call": False,
        "description": "A timeless haircut that suits your style and preferences. Our experienced barbers will give you a fresh look.",
        "price": {
            "currency": {
                "code": "CAD",
                "symbol": "CA$",
                "name": "Canadian Dollar"
            },
            "amount": "35.00"
        },
        "images": None
    }

    # CLEAN UP
    c_res = await client.delete(f'/api/services/delete/{service_id}', headers=headers)
    assert c_res.status_code == 200


# TEST DELETE SERVICE
@pytest.mark.anyio
async def test_delete_service(client: AsyncClient, get_token: str, clean_profile_state):
    # SETUP
    headers = {'Authorization': f'Bearer {get_token}'}
    setup_response = await client.post(url='/api/merchant/create', headers=headers, json={
        "username": "suavbarber898",
        "name": "Tshiamo's Barbershop",
        "profession": "Barber",
        "location": {
            "coordinates": {
                "longitude": -79.88573989999999,
                "latitude": 43.5111844
            },
            "country": {
                "name": "South Africa",
                "code": "ZA",
                "currency": {
                    "code": "ZAR",
                    "symbol": "R",
                    "name": "South African Rand"
                }
            },
            "city": "Milton",
            "street_address": "123 Main St E, Milton, ON L9T 1N4, Canada"
        },
        "bio": "Discover the art of grooming at BarberShop XYZ in Toronto, Canada. Our skilled barbers deliver precision haircuts, expert shaves, and a relaxing experience. Book today and elevate your style."
    })
    assert setup_response.status_code == 201

    payload = {
        "service_name": "Classic Haircut",
        "duration_minutes": 45,
        "out_call": False,
        "description": "A timeless haircut that suits your style and preferences. Our experienced barbers will give you a fresh look.",
        "price": {
            "currency": {
                "code": "CAD",
                "symbol": "CA$",
                "name": "Canadian Dollar"
            },
            "amount": "25.00"
        }
    }
    setup_service_response = await client.post("/api/services/create", headers=headers, json=payload)
    json_response = setup_service_response.json()
    assert setup_service_response.status_code == 201
    assert '_id' in json_response
    assert isinstance(json_response['_id'], str)
    service_id = json_response['_id']
    assert len(service_id) > 0

    # TEST
    response = await client.delete(f'/api/services/delete/{service_id}', headers=headers)
    assert response.status_code == 200
    assert response.json() == {"message": "Service deleted successfully."}

    get_service = await client.get(f'/api/services/get/{service_id}')
    assert get_service.status_code == 404
    assert get_service.json() == {'detail': 'Service not found.'}


@pytest.mark.anyio
async def test_get_my_services(client: AsyncClient, get_token: str, clean_profile_state):
    # SETUP
    payload_1 = {
        "service_name": "Classic Haircut",
        "duration_minutes": 45,
        "out_call": False,
        "description": "A timeless haircut that suits your style and preferences. Our experienced barbers will give you a fresh look.",
        "price": {
            "currency": {
                "code": "CAD",
                "symbol": "CA$",
                "name": "Canadian Dollar"
            },
            "amount": "25.00"
        }
    }
    payload_2 = {
        "service_name": "Out-call Wedding Package",
        "duration_minutes": 180,
        "customisation": "true",
        "description": "Let us bring our professional barber services to your wedding venue. We'll ensure the groom and groomsmen look their best.",
        "price": {
            "currency": {
                "code": "CAD",
                "symbol": "CA$",
                "name": "Canadian Dollar"
            },
            "amount": "350.00"
        }
    }

    # SETUP CREATE MERCHANT_PROFILE
    headers = {'Authorization': f'Bearer {get_token}'}
    setup_response = await client.post(url='/api/merchant/create', headers=headers, json={
        "username": "suavbarber898",
        "name": "Tshiamo's Barbershop",
        "profession": "Barber",
        "location": {
            "coordinates": {
                "longitude": -79.88573989999999,
                "latitude": 43.5111844
            },
            "country": {
                "name": "South Africa",
                "code": "ZA",
                "currency": {
                    "code": "ZAR",
                    "symbol": "R",
                    "name": "South African Rand"
                }
            },
            "city": "Milton",
            "street_address": "123 Main St E, Milton, ON L9T 1N4, Canada"
        },
        "bio": "Discover the art of grooming at BarberShop XYZ in Toronto, Canada. Our skilled barbers deliver precision haircuts, expert shaves, and a relaxing experience. Book today and elevate your style."
    })
    assert setup_response.status_code == 201

    # SETUP CREATE 2 SERVICES
    setup_service_1 = await client.post(
        '/api/services/create', headers=headers, json=payload_1)
    assert setup_service_1.status_code == 201
    service1_json_response = setup_service_1.json()
    assert '_id' in service1_json_response
    assert isinstance(service1_json_response['_id'], str)
    service1_id = service1_json_response['_id']
    assert len(service1_id) > 0

    setup_service_2 = await client.post(
        '/api/services/create', headers=headers, json=payload_2)
    assert setup_service_2.status_code == 201
    service2_json_response = setup_service_2.json()
    assert '_id' in service2_json_response
    assert isinstance(service2_json_response['_id'], str)
    service2_id = service2_json_response['_id']
    assert len(service2_id) > 0

    # TEST
    response = await client.get('/api/services/get_my_services', headers=headers)
    assert response.status_code == 200
    assert response.json() == [
        {

            "_id": service1_id,
            "service_name": "Classic Haircut",
            "duration_minutes": 45,
            "out_call": False,
            "description": "A timeless haircut that suits your style and preferences. Our experienced barbers will give you a fresh look.",
            "price": {
                "currency": {
                    "code": "CAD",
                    "symbol": "CA$",
                    "name": "Canadian Dollar"
                },
                "amount": "25.00"
            },
            "images": None

        },
        {
            '_id': service2_id,
            "service_name": "Out-call Wedding Package",
            "duration_minutes": 180,
            "out_call": False,
            "description": "Let us bring our professional barber services to your wedding venue. We'll ensure the groom and groomsmen look their best.",
            "price": {
                "currency": {
                    "code": "CAD",
                    "symbol": "CA$",
                    "name": "Canadian Dollar"
                },
                "amount": "350.00"
            },
            'images': None
        }
    ]

    # CLEAN UP
    c_res = await client.delete(f'/api/services/delete/{service1_id}', headers=headers)
    assert c_res.status_code == 200

    # CLEAN UP
    c_res = await client.delete(f'/api/services/delete/{service2_id}', headers=headers)
    assert c_res.status_code == 200

# TEST UPDATE SERVICE THAT ISN'T YOURS


@pytest.mark.anyio
async def test_update_other_merchants_service_not_allowed(client: AsyncClient, get_token, clean_profile_state):
    pass
    # assert False

# TEST DELETE SERVICE THAT ISN'T YOURS NOT ALLOWED


@pytest.mark.anyio
async def test_delete_other_merchants_service_not_allowed(client: AsyncClient, get_token, clean_profile_state):
    # assert False
    pass


@pytest.mark.anyio
async def test_get_all_services(client: AsyncClient):
    # assert False
    pass
# ----------------------------------- #
# ========= SEARCH SERVICES ========= #

# SEARCH BY FILTER -> COUNTRY
# SEARCH BY FILTER -> MIN PRICE
# SEARCH BY FILTER -> MAX PRICE
# SEARCH BY FILTER -> PRICE RANGE
# SEARCH BY FILTER -> CATEGORY

# SEARCH BY FILTER -> KEYWORD
# ====== (SERVICE NAME / SOMETHING IN DESCRIPTION)

# ----------------------------------- #
