import pytest
import requests
from httpx import ASGITransport, AsyncClient
# from typing import Dict, Generator
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from app.config.database.database import get_db, get_db_client, get_db_name
from tests.data.data_setup import merchant_card_response
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


# TEST GET NON EXISITENT MERCHANT
@pytest.mark.anyio
async def test_get_non_existent_merchant(client: AsyncClient, get_token: str):

    headers = {'Authorization': f'Bearer {get_token}'}
    response = await client.get(url='/api/merchant/get-my-profile', headers=headers)
    assert response.status_code == 404
    assert response.json() == {
        'detail': 'Merchant profile does not exist. Please create one.'}

# TEST CREATE MERCHANT PROFILE


@pytest.mark.anyio
async def test_create_merchant_profile(client: AsyncClient, get_token: str, clean_profile_state):

    headers = {'Authorization': f'Bearer {get_token}'}
    response = await client.post(url='/api/merchant/create', headers=headers, json={
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

    assert response.status_code == 201
    assert response.json() == {
        "name": "Tshiamo's Barbershop",
        "username": "suavbarber898",
        "profession": "Barber",
        "location": {
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
            "street_address": "123 Main St E, Milton, ON L9T 1N4, Canada",
            "coordinates": {
                "longitude": -79.88573989999999,
                "latitude": 43.5111844
            }
        },
        "profile_image_url": None,
        "schedule": {
            "daily_schedule": {
                "monday": {
                    "is_available": False,
                    "operating_hours": {
                        "start_time": None,
                        "end_time": None
                    },
                    "blocked_hours": []
                },
                "tuesday": {
                    "is_available": False,
                    "operating_hours": {
                        "start_time": None,
                        "end_time": None
                    },
                    "blocked_hours": []
                },
                "wednesday": {
                    "is_available": False,
                    "operating_hours": {
                        "start_time": None,
                        "end_time": None
                    },
                    "blocked_hours": []
                },
                "thursday": {
                    "is_available": False,
                    "operating_hours": {
                        "start_time": None,
                        "end_time": None
                    },
                    "blocked_hours": []
                },
                "friday": {
                    "is_available": False,
                    "operating_hours": {
                        "start_time": None,
                        "end_time": None
                    },
                    "blocked_hours": []
                },
                "saturday": {
                    "is_available": False,
                    "operating_hours": {
                        "start_time": None,
                        "end_time": None
                    },
                    "blocked_hours": []
                },
                "sunday": {
                    "is_available": False,
                    "operating_hours": {
                        "start_time": None,
                        "end_time": None
                    },
                    "blocked_hours": []
                }
            },
            "blocked_dates": []
        },
        "bio": "Discover the art of grooming at BarberShop XYZ in Toronto, Canada. Our skilled barbers deliver precision haircuts, expert shaves, and a relaxing experience. Book today and elevate your style.",
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

# TEST GET EXISTING MERCHANT PROFILE


@pytest.mark.anyio
async def test_get_existing_merchant_profile(client: AsyncClient, get_token: str, clean_profile_state):

    headers = {'Authorization': f'Bearer {get_token}'}
    await client.post(url='/api/merchant/create', headers=headers, json={
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

    response = await client.get(url='/api/merchant/get-my-profile', headers=headers)
    assert response.status_code == 200
    assert response.json() == {
        "name": "Tshiamo's Barbershop",
        "username": "suavbarber898",
        "profession": "Barber",
        "location": {
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
            "street_address": "123 Main St E, Milton, ON L9T 1N4, Canada",
            "coordinates": {
                "longitude": -79.88573989999999,
                "latitude": 43.5111844
            }
        },
        "profile_image_url": None,
        "schedule": {
            "daily_schedule": {
                "monday": {
                    "is_available": False,
                    "operating_hours": {
                        "start_time": None,
                        "end_time": None
                    },
                    "blocked_hours": []
                },
                "tuesday": {
                    "is_available": False,
                    "operating_hours": {
                        "start_time": None,
                        "end_time": None
                    },
                    "blocked_hours": []
                },
                "wednesday": {
                    "is_available": False,
                    "operating_hours": {
                        "start_time": None,
                        "end_time": None
                    },
                    "blocked_hours": []
                },
                "thursday": {
                    "is_available": False,
                    "operating_hours": {
                        "start_time": None,
                        "end_time": None
                    },
                    "blocked_hours": []
                },
                "friday": {
                    "is_available": False,
                    "operating_hours": {
                        "start_time": None,
                        "end_time": None
                    },
                    "blocked_hours": []
                },
                "saturday": {
                    "is_available": False,
                    "operating_hours": {
                        "start_time": None,
                        "end_time": None
                    },
                    "blocked_hours": []
                },
                "sunday": {
                    "is_available": False,
                    "operating_hours": {
                        "start_time": None,
                        "end_time": None
                    },
                    "blocked_hours": []
                }
            },
            "blocked_dates": []
        },
        "bio": "Discover the art of grooming at BarberShop XYZ in Toronto, Canada. Our skilled barbers deliver precision haircuts, expert shaves, and a relaxing experience. Book today and elevate your style.",
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

# TEST ONLY ONE MERCHANT ACCOUNT ALLOWE


@pytest.mark.anyio
async def test_create_second_merchant_account_not_allowed(client: AsyncClient, get_token: str, clean_profile_state):
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
    response = await client.post(url='/api/merchant/create', headers=headers, json={
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
    assert response.status_code == 409
    assert response.json() == {
        'detail': 'Merchant Profile Already Exists. Update Instead.'
    }

# TEST UPDATE MERCHANT PROFILE


@pytest.mark.anyio
async def test_update_merchant_profile(client: AsyncClient, get_token: str, clean_profile_state):
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
    response = await client.put(url='/api/merchant/update/update_merchant_profile', headers=headers, json={
        "username": "suavbarber5",
        "name": "Tshiamo's Barbershop in Canada",
        "profession": "Barber",
        "location": {
            "coordinates": {
                "longitude": -79.88573989999999,
                "latitude": 43.5111844
            },
            "country": {
                "name": "Canada",
                "code": "CA",
                "currency": {
                    "code": "CAD",
                    "symbol": "CA$",
                    "name": "Canadian Dollar"
                }
            },
            "city": "Milton",
            "street_address": "123 Main St E, Milton, ON L9T 1N4, Canada"
        },

        "bio": "Discover the art of grooming at BarberShop XYZ in Toronto, Canada. Our skilled barbers deliver precision haircuts, expert shaves, and a relaxing experience. Book today and elevate your style."
    })
    assert response.status_code == 200
    assert response.json() == {
        "name": "Tshiamo's Barbershop in Canada",
        "username": "suavbarber5",
        "profession": "Barber",
        "location": {
            "country": {
                "name": "Canada",
                "code": "CA",
                "currency": {
                    "code": "CAD",
                    "symbol": "CA$",
                    "name": "Canadian Dollar"
                }
            },
            "city": "Milton",
            "street_address": "123 Main St E, Milton, ON L9T 1N4, Canada",
            "coordinates": {
                "longitude": -79.88573989999999,
                "latitude": 43.5111844
            }
        },
        "profile_image_url": None,
        "schedule": {
            "daily_schedule": {
                "monday": {
                    "is_available": False,
                    "operating_hours": {
                        "start_time": None,
                        "end_time": None
                    },
                    "blocked_hours": []
                },
                "tuesday": {
                    "is_available": False,
                    "operating_hours": {
                        "start_time": None,
                        "end_time": None
                    },
                    "blocked_hours": []
                },
                "wednesday": {
                    "is_available": False,
                    "operating_hours": {
                        "start_time": None,
                        "end_time": None
                    },
                    "blocked_hours": []
                },
                "thursday": {
                    "is_available": False,
                    "operating_hours": {
                        "start_time": None,
                        "end_time": None
                    },
                    "blocked_hours": []
                },
                "friday": {
                    "is_available": False,
                    "operating_hours": {
                        "start_time": None,
                        "end_time": None
                    },
                    "blocked_hours": []
                },
                "saturday": {
                    "is_available": False,
                    "operating_hours": {
                        "start_time": None,
                        "end_time": None
                    },
                    "blocked_hours": []
                },
                "sunday": {
                    "is_available": False,
                    "operating_hours": {
                        "start_time": None,
                        "end_time": None
                    },
                    "blocked_hours": []
                }
            },
            "blocked_dates": []
        },
        "bio": "Discover the art of grooming at BarberShop XYZ in Toronto, Canada. Our skilled barbers deliver precision haircuts, expert shaves, and a relaxing experience. Book today and elevate your style.",
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

# TEST UPDATE MERCHANT BASIC INFO


@pytest.mark.anyio
async def test_update_merchant_basic_info(client: AsyncClient, get_token: str, clean_profile_state):
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
    response = await client.put(url='/api/merchant/update/basic-info', headers=headers, json={
        "username": "suavbarber5",
        "name": "Tshiamo's Barbershop in Canada",
        "profession": "Barber",
        "bio": "Hello"
    })
    assert response.status_code == 200
    assert response.json() == {
        "name": "Tshiamo's Barbershop in Canada",
        "username": "suavbarber5",
        "profession": "Barber",
        "location": {
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
            "street_address": "123 Main St E, Milton, ON L9T 1N4, Canada",
            "coordinates": {
                "longitude": -79.88573989999999,
                "latitude": 43.5111844
            }
        },
        "profile_image_url": None,
        "schedule": {
            "daily_schedule": {
                "monday": {
                    "is_available": False,
                    "operating_hours": {
                        "start_time": None,
                        "end_time": None
                    },
                    "blocked_hours": []
                },
                "tuesday": {
                    "is_available": False,
                    "operating_hours": {
                        "start_time": None,
                        "end_time": None
                    },
                    "blocked_hours": []
                },
                "wednesday": {
                    "is_available": False,
                    "operating_hours": {
                        "start_time": None,
                        "end_time": None
                    },
                    "blocked_hours": []
                },
                "thursday": {
                    "is_available": False,
                    "operating_hours": {
                        "start_time": None,
                        "end_time": None
                    },
                    "blocked_hours": []
                },
                "friday": {
                    "is_available": False,
                    "operating_hours": {
                        "start_time": None,
                        "end_time": None
                    },
                    "blocked_hours": []
                },
                "saturday": {
                    "is_available": False,
                    "operating_hours": {
                        "start_time": None,
                        "end_time": None
                    },
                    "blocked_hours": []
                },
                "sunday": {
                    "is_available": False,
                    "operating_hours": {
                        "start_time": None,
                        "end_time": None
                    },
                    "blocked_hours": []
                }
            },
            "blocked_dates": []
        },
        "bio": "Hello",
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
async def test_update_merchant_location_only(client: AsyncClient, get_token: str, clean_profile_state):
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
    response = await client.put(url='/api/merchant/update/location-info', headers=headers, json={
        "coordinates": {
            "longitude": -75.67536679999999,
            "latitude": 45.3803878
        },
        "country": {
            "name": "Canada",
            "code": "CA",
            "currency": {
                    "code": "CAD",
                    "symbol": "CA$",
                    "name": "Canadian Dollar"
            }
        },
        "city": "Ottawa",
        "street_address": "1059 Aldea Ave, Ottawa, ON K1H 8B8, Canada"
    })
    assert response.status_code == 200
    assert response.json() == {
        "name": "Tshiamo's Barbershop",
        "username": "suavbarber898",
        "profession": "Barber",
        "location": {
            "country": {
                "name": "Canada",
                "code": "CA",
                "currency": {
                    "code": "CAD",
                    "symbol": "CA$",
                    "name": "Canadian Dollar"
                }
            },
            "city": "Ottawa",
            "street_address": "1059 Aldea Ave, Ottawa, ON K1H 8B8, Canada",
            "coordinates": {
                "longitude": -75.67536679999999,
                "latitude": 45.3803878
            }
        },
        "profile_image_url": None,
        "schedule": {
            "daily_schedule": {
                "monday": {
                    "is_available": False,
                    "operating_hours": {
                        "start_time": None,
                        "end_time": None
                    },
                    "blocked_hours": []
                },
                "tuesday": {
                    "is_available": False,
                    "operating_hours": {
                        "start_time": None,
                        "end_time": None
                    },
                    "blocked_hours": []
                },
                "wednesday": {
                    "is_available": False,
                    "operating_hours": {
                        "start_time": None,
                        "end_time": None
                    },
                    "blocked_hours": []
                },
                "thursday": {
                    "is_available": False,
                    "operating_hours": {
                        "start_time": None,
                        "end_time": None
                    },
                    "blocked_hours": []
                },
                "friday": {
                    "is_available": False,
                    "operating_hours": {
                        "start_time": None,
                        "end_time": None
                    },
                    "blocked_hours": []
                },
                "saturday": {
                    "is_available": False,
                    "operating_hours": {
                        "start_time": None,
                        "end_time": None
                    },
                    "blocked_hours": []
                },
                "sunday": {
                    "is_available": False,
                    "operating_hours": {
                        "start_time": None,
                        "end_time": None
                    },
                    "blocked_hours": []
                }
            },
            "blocked_dates": []
        },
        "bio": "Discover the art of grooming at BarberShop XYZ in Toronto, Canada. Our skilled barbers deliver precision haircuts, expert shaves, and a relaxing experience. Book today and elevate your style.",
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
async def test_update_merchant_basic_info_without_profile_shows_not_found(client: AsyncClient, get_token: str, clean_profile_state):
    headers = {'Authorization': f'Bearer {get_token}'}
 # TEST
    response = await client.put(url='/api/merchant/update/basic-info', headers=headers, json={
        "username": "suavbarber5",
        "name": "Tshiamo's Barbershop in Canada",
        "profession": "Barber",
        "bio": "Hello"
    })
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Merchant profile does not exist. Please create one."}


@pytest.mark.anyio
async def test_update_merchant_location_with_no_profile_shows_not_found(client: AsyncClient, get_token: str, clean_profile_state):
    headers = {'Authorization': f'Bearer {get_token}'}
    # TEST
    response = await client.put(url='/api/merchant/update/location-info', headers=headers, json={
        "coordinates": {
            "longitude": -75.67536679999999,
            "latitude": 45.3803878
        },
        "country": {
            "name": "Canada",
            "code": "CA",
            "currency": {
                    "code": "CAD",
                    "symbol": "CA$",
                    "name": "Canadian Dollar"
            }
        },
        "city": "Ottawa",
        "street_address": "1059 Aldea Ave, Ottawa, ON K1H 8B8, Canada"
    })
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Merchant profile does not exist. Please create one."}


@pytest.mark.anyio
async def test_update_merchant_profile_with_no_profile_shows_not_found(client: AsyncClient, get_token: str, clean_profile_state):
    headers = {'Authorization': f'Bearer {get_token}'}
    # TEST
    response = await client.put(url='/api/merchant/update/update_merchant_profile', headers=headers, json={
        "username": "suavbarber5",
        "name": "Tshiamo's Barbershop in Canada",
        "profession": "Barber",
        "location": {
            "coordinates": {
                "longitude": -79.88573989999999,
                "latitude": 43.5111844
            },
            "country": {
                "name": "Canada",
                "code": "CA",
                "currency": {
                    "code": "CAD",
                    "symbol": "CA$",
                    "name": "Canadian Dollar"
                }
            },
            "city": "Milton",
            "street_address": "123 Main St E, Milton, ON L9T 1N4, Canada"
        },

        "bio": "Discover the art of grooming at BarberShop XYZ in Toronto, Canada. Our skilled barbers deliver precision haircuts, expert shaves, and a relaxing experience. Book today and elevate your style."
    })
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Merchant profile does not exist. Please create one."}


# TEST UPDATE MERCHANT DATA WITH NO NEW INFORMATION

# TEST UPDATE USERNAME TO EXISTING USERNAME NOT ALLOWED

# TEST DELETE MERCHANT PROFILE
@pytest.mark.anyio
async def test_delete_merchant_profile(client: AsyncClient, get_token: str, clean_profile_state):
    headers = {'Authorization': f'Bearer {get_token}'}
    # SETUP
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
    response = await client.delete(url='/api/merchant/delete', headers=headers)
    assert response.status_code == 200
    assert response.json() == {
        "detail": "Merchant profile and associated username deleted successfully."}

# TEST DELETE MERCHANT ALSO DELETES USERNAME RECORD


@pytest.mark.anyio
async def test_delete_merchant_profile_also_deletes_username_record(client: AsyncClient, get_token: str, clean_profile_state):
    headers = {'Authorization': f'Bearer {get_token}'}
    # SETUP
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
    response = await client.delete(url='/api/merchant/delete', headers=headers)
    assert response.status_code == 200
    assert response.json() == {
        "detail": "Merchant profile and associated username deleted successfully."}

    # Check if username record is now available
    response = await client.get(url='/api/merchant/get-my-profile', headers=headers)
    assert response.status_code == 404
    assert response.json() == {
        'detail': 'Merchant profile does not exist. Please create one.'}
# TEST UPDATE SCHEDULE


def get_example_schedule():
    return {
        "daily_schedule": {
            "monday": {
                "is_available": True,
                "operating_hours": {
                    "start_time": "10:00:00Z",
                    "end_time": "18:00:00Z"
                },
                "blocked_hours": [
                    {
                        "start_time": "14:00:00Z",
                        "end_time": "15:00:00Z"
                    }
                ]
            },
            "tuesday": {
                "is_available": True,
                "operating_hours": {
                    "start_time": "10:00:00Z",
                    "end_time": "18:00:00Z"
                },
                "blocked_hours": [
                    {
                        "start_time": "14:00:00Z",
                        "end_time": "15:00:00Z"
                    }
                ]
            },
            "wednesday": {
                "is_available": True,
                "operating_hours": {
                    "start_time": "10:00:00Z",
                    "end_time": "18:00:00Z"
                },
                "blocked_hours": []
            },
            "thursday": {
                "is_available": True,
                "operating_hours": {
                    "start_time": "10:00:00Z",
                    "end_time": "18:00:00Z"
                },
                "blocked_hours": []
            },
            "friday": {
                "is_available": True,
                "operating_hours": {
                    "start_time": "10:00:00Z",
                    "end_time": "18:00:00Z"
                },
                "blocked_hours": []
            },
            "saturday": {
                "is_available": True,
                "operating_hours": {
                    "start_time": "11:00:00Z",
                    "end_time": "16:00:00Z"
                },
                "blocked_hours": []
            },
            "sunday": {
                "is_available": False,
                "operating_hours": {
                    "start_time": None,
                    "end_time": None
                },
                "blocked_hours": []
            }
        },
        "blocked_dates": [
            "2024-12-25",
            "2025-01-01"
        ]
    }


@pytest.mark.anyio
async def test_update_availability(client: AsyncClient, get_token: str, clean_profile_state):
    headers = {'Authorization': f'Bearer {get_token}'}
    # SETUP
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

    response = await client.put('/api/merchant/update/availability', headers=headers, json=get_example_schedule())

    assert response.status_code == 200
    assert response.json() == {
        "daily_schedule": {
            "monday": {
                "is_available": True,
                "operating_hours": {
                    "start_time": "10:00:00Z",
                    "end_time": "18:00:00Z"
                },
                "blocked_hours": [
                    {
                        "start_time": "14:00:00Z",
                        "end_time": "15:00:00Z"
                    }
                ]
            },
            "tuesday": {
                "is_available": True,
                "operating_hours": {
                    "start_time": "10:00:00Z",
                    "end_time": "18:00:00Z"
                },
                "blocked_hours": [
                    {
                        "start_time": "14:00:00Z",
                        "end_time": "15:00:00Z"
                    }
                ]
            },
            "wednesday": {
                "is_available": True,
                "operating_hours": {
                    "start_time": "10:00:00Z",
                    "end_time": "18:00:00Z"
                },
                "blocked_hours": []
            },
            "thursday": {
                "is_available": True,
                "operating_hours": {
                    "start_time": "10:00:00Z",
                    "end_time": "18:00:00Z"
                },
                "blocked_hours": []
            },
            "friday": {
                "is_available": True,
                "operating_hours": {
                    "start_time": "10:00:00Z",
                    "end_time": "18:00:00Z"
                },
                "blocked_hours": []
            },
            "saturday": {
                "is_available": True,
                "operating_hours": {
                    "start_time": "11:00:00Z",
                    "end_time": "16:00:00Z"
                },
                "blocked_hours": []
            },
            "sunday": {
                "is_available": False,
                "operating_hours": {
                    "start_time": None,
                    "end_time": None
                },
                "blocked_hours": []
            }
        },
        "blocked_dates": [
            "2024-12-25",
            "2025-01-01"
        ]
    }


# TEST DELETE MERCHANT PROFILE WITH NO PROFILE
@pytest.mark.anyio
async def test_delete_merchant_profile_with_no_profile_shows_not_found(client: AsyncClient, get_token: str, clean_profile_state):
    headers = {'Authorization': f'Bearer {get_token}'}
    # TEST
    response = await client.delete(url='/api/merchant/delete', headers=headers)
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Merchant profile not found."}


# TEST GET ALL MERCHANT CARDS
@pytest.mark.anyio
async def test_get_all_merchants(client: AsyncClient, get_token: str, clean_profile_state):
    # [TODO]: SETUP INSERT MANY MERCHANTS (3)

    response = await client.get('/api/merchants/cards')
    assert response.status_code == 200
    assert response.json() == merchant_card_response


# VERIFY DELETED MERCHANT PROFILE IS NOT IN RESULTS OF GET ALL MERCHANT CARD DATA
# insert many merchants
# insert new one for me
# retrieve all merchants
# delete merchants
# get new list of merchants

# TEST DUPLICATE USERNAME NOT ALLOWED
# insert many merchants
# create new merchant with occupied username.
# update merchant username to occupied username

# TEST NO USERNAME RECORD OR MERCHANT RECORD EXISTS IF DUPLICATE USERNAME
# insert many merchants
# occupy username.
# error in inserting merchant
# check username
# haha
#
# TEST GET MERCHANT PUBLIC PROFILE INFO
# get merchant by username
