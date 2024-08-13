import asyncio
import requests
from pydantic_settings import SettingsConfigDict, BaseSettings
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClient
from pymongo.server_api import ServerApi
import certifi
ca = certifi.where()


class Env(BaseSettings):
    auth0_domain:             str  # Tenant domain
    # API identifier that serves the applications (fastapi instance)
    auth0_api_audience:       str
    auth0_api_audience_wrong: str
    auth0_expired_token:      str
    auth0_wrong_tenant_token: str
    auth0_m2m_client_id:      str   # Machine-to-machine Application
    auth0_m2m_client_secret:  str
    auth0_spa_client_id:      str   # Single Page Application
    auth0_spa_client_secret:  str
    auth0_spa_username:       str
    auth0_spa_password:       str
    auth0_test_permission:    str

    test_db_name: str
    test_db_url: str
    model_config = SettingsConfigDict(env_file='.env.test')


env = Env()


def generate_access_token():
    resp = requests.post(
        f'https://{env.auth0_domain}/oauth/token',
        headers={'content-type': 'application/x-www-form-urlencoded'},
        data={
            'grant_type': 'password',
            'username': env.auth0_spa_username,
            'password': env.auth0_spa_password,
            'client_id': env.auth0_spa_client_id,
            'client_secret': env.auth0_spa_client_secret,
            'audience': env.auth0_api_audience,
        })
    assert resp.status_code == 200, resp.text
    return resp.json()['access_token']
