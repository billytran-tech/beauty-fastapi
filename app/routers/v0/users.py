from pydantic import ConfigDict, BaseModel
from twilio.rest import Client
import random
from typing import List
from fastapi import APIRouter, HTTPException, Depends, status, Depends
from fastapi.encoders import jsonable_encoder
from app.config.config import settings
from app.schema.object_models.v0 import service_model
from app.auth.auth import Auth0, Auth0User
from app.config.database.database import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.helpers.country_data import get_country
from app.schema.object_models.v0.user_model import RegisterUser, UserProfile, UserProfileResponse
from app.schema.object_models.v0.contact_model import ContactInfo
from app.schema.object_models.v0.country_model import FullCountryModel

router = APIRouter(
    prefix='/api/users',
    tags=['User Details']
)

auth = Auth0(domain=settings.AUTH0_DOMAIN,
             api_audience=settings.AUTH0_API_AUDIENCE, scopes={})

twilio_sid = settings.TWILIO_SID
twilio_token = settings.TWILIO_TOKEN
twilio_verification_sid = settings.TWILIO_VERIFICATION_SID


@router.post('/register', response_model=UserProfileResponse)
async def register_user(payload: RegisterUser, user_profile: Auth0User = Depends(auth.get_user), db: AsyncIOMotorDatabase = Depends(get_db)):

    user_exits = await db['users'].find_one({'user_id': user_profile.id})
    if (user_exits):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail='Profile Already Exists.')
    country = get_country(payload.country_code)
    if not country:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid Country Code')
    country = FullCountryModel.model_validate(country)

    contact_info = {
        'phone_number': {
            'dialing_code': country.dialing_code,
            'phone_number': payload.phone_number
        }
    }
    user = {
        '_id': str(payload.id),
        'first_name': payload.first_name,
        'last_name': payload.last_name,
        'user_id': user_profile.id,
        'country_code': payload.country_code,
        'contact_info': contact_info
    }

    user = UserProfile.model_validate(user)
    user = jsonable_encoder(user)
    new_user = await db['users'].insert_one(user)
    created_user = await db['users'].find_one({'_id': new_user.inserted_id})

    created_user = UserProfile.model_validate(created_user)
    country_code = created_user.country_code
    created_user = created_user.model_dump()
    created_user['country'] = get_country(country_code)
    user_response = UserProfileResponse.model_validate(created_user)
    return user_response


@router.get('/', response_model=UserProfileResponse)
async def get_user_profile(user_profile: Auth0User = Depends(auth.get_user), db: AsyncIOMotorDatabase = Depends(get_db)):
    user = await db['users'].find_one({'user_id': user_profile.id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='User Not Found.')
    user = UserProfile.model_validate(user)
    country = get_country(user.country_code)
    user = jsonable_encoder(user)
    user['country'] = country

    user_response = UserProfileResponse.model_validate(user)
    return user_response


@router.get('/verification-status/phone')
async def get_phone_number_verification_status(user_profile: Auth0User = Depends(auth.get_user), db: AsyncIOMotorDatabase = Depends(get_db)):

    user = await db['users'].find_one({'user_id': user_profile.id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='User Not Found.')

    user = UserProfile.model_validate(user)

    verification_status = user.contact_info.phone_number.is_verified

    return {'is_verified': verification_status}


def get_twilio_client():
    return Client(twilio_sid, twilio_token)


def get_verification_service_id():
    return twilio_verification_sid


def start_verification_process(phone_number: str, twilio_client: Client):
    client = twilio_client
    verification = client.verify.v2.services(
        get_verification_service_id()).verifications.create(to=phone_number, channel="sms")
    return verification.status


def attempt_verification(phone_number: str, code: str, twilio_client: Client):
    client = twilio_client

    verification_check = client.verify.v2.services(
        get_verification_service_id()).verification_checks.create(to=phone_number, code=code)
    return verification_check.status


@router.get('/verify-request/send-otp')
async def send_otp_for_verification(user_profile: Auth0User = Depends(auth.get_user), db: AsyncIOMotorDatabase = Depends(get_db)):
    user = await db['users'].find_one({'user_id': user_profile.id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='User Not Found.')

    user = UserProfile.model_validate(user)
    verification_status = user.contact_info.phone_number.is_verified
    if (verification_status):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail='Phone Number is Already Verified')

    phone_number_object = user.contact_info.phone_number
    phone_number_string = phone_number_object.dialing_code + \
        str(phone_number_object.phone_number)

    start_verification_process(phone_number_string)

    return {'message': 'OTP Sent'}


class OTP(BaseModel):
    code: str
    model_config = ConfigDict(populate_by_name=True,
                              arbitrary_types_allowed=True)


@router.post('/submit-otp')
async def submit_otp(payload: OTP, user_profile: Auth0User = Depends(auth.get_user), db: AsyncIOMotorDatabase = Depends(get_db)):
    user = await db['users'].find_one({'user_id': user_profile.id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='User Not Found.')

    user = UserProfile.model_validate(user)
    verification_status = user.contact_info.phone_number.is_verified
    if (verification_status):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail='Phone Number is Already Verified')

    phone_number_object = user.contact_info.phone_number
    phone_number_string = phone_number_object.dialing_code + \
        str(phone_number_object.phone_number)

    result = attempt_verification(phone_number_string, payload.code)
    if (result == "approved"):
        updated_result = await db['users'].update_one({'user_id': user_profile.id}, {'$set': {'contact_info.phone_number.is_verified': True}})
        if updated_result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND)
        if updated_result.modified_count == 0:
            raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED)

        return {'message': 'Verification Successful'}
    else:
        return {'message': 'Verification Not Succesful'}
