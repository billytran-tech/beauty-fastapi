import random
from typing import List
from fastapi import APIRouter, HTTPException, Depends, status, Depends
from fastapi.encoders import jsonable_encoder
from app.config.config import settings
from app.schema.object_models.v0 import service_model
from app.auth.auth import Auth0, Auth0User
from app.config.database.database import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.helpers.country_data import get_country, list_available_countries
from app.schema.object_models.v0.country_model import CountrySummary

router = APIRouter(
    prefix='/api/country',
    tags=['Country Details']
)

auth = Auth0(domain=settings.AUTH0_DOMAIN,
             api_audience=settings.AUTH0_API_AUDIENCE, scopes={})


@router.get('/available', response_model=List[CountrySummary])
def get_available_countries():
    return list_available_countries()


# @router.get('/code/{country_code}')
# def get_country_data(country_code: str):
#     country_code = country_code.upper()
#     return get_country(country_code)
