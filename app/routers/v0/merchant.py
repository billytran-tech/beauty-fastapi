import logging
from datetime import time
from typing import Annotated, List
from fastapi import APIRouter, Query, status, Depends, HTTPException, Security
from fastapi.encoders import jsonable_encoder
from pydantic import ConfigDict, BaseModel, Field
import pymongo
import pymongo.errors
from pymongo.errors import PyMongoError

from app.config.config import settings
from app.helpers.default_user_data import get_default_notification_settings, get_default_schedule
from app.schema.object_models.v0 import user_model, service_model
from app.schema.object_models.v0.id_model import PyObjectId
from app.config.database.database import get_db, get_db_client, get_db_name
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClient
from app.auth.auth import Auth0, Auth0User


router = APIRouter(
    prefix='/api/merchant',
    tags=['Merchant Profile']
)

auth0_domain = settings.AUTH0_DOMAIN
auth0_api_audience = settings.AUTH0_API_AUDIENCE
auth = Auth0(domain=auth0_domain, api_audience=auth0_api_audience, scopes={})
db_name = settings.DB_NAME


class CreateUserName(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    username: str
    user_auth0_id: str
    model_config = ConfigDict(populate_by_name=True,
                              arbitrary_types_allowed=True)


@router.get('/', status_code=status.HTTP_200_OK, response_model=List[user_model.MerchantCardResponse])
async def get_merchants(
    page: Annotated[int, Query(description="Page Number")] = 1,
    per_page: Annotated[int, Query(
        description="Number of items per page")] = 10,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    if page < 1 or per_page < 1:
        raise HTTPException(
            status_code=400, detail="Invalid page or per_page values")

    # Calculate the number of documents to skip
    skip = (page - 1) * per_page

    # QueryMongoDB using skip and limit
    try:
        merchants = await db['merchants'].find().skip(skip).limit(per_page).to_list(length=None)
        # users = jsonable_encoder(users)
        # return users
        # print(users)
        merchant_profiles = []
        for merchant in merchants:

            username = await db['usernames'].find_one({'_id': merchant.get('username_id')})
            merchantCardData = {
                'username': username.get('username'),
                'image_url': merchant.get('profile_image_url'),
                'header_name': merchant.get('name'),
                'location': merchant.get('location'),
                'profession': merchant.get('profession'),
            }
            user_model.MerchantCardResponse.model_validate(
                merchantCardData)
            merchant_profiles.append(merchantCardData)

        return merchant_profiles

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{e}")


@router.get('/get-my-profile', status_code=status.HTTP_200_OK, dependencies=[Depends(auth.implicit_scheme)], response_model=user_model.MerchantProfileData)
async def get_my_profile(user_profile: Auth0User = Depends(auth.get_user), db: AsyncIOMotorDatabase = Depends(get_db)):
    try:
        user_id = user_profile.id
        merchant = await db['merchants'].find_one({'user_id': user_id})
        if not merchant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Merchant profile does not exist. Please create one.")

        merchant = jsonable_encoder(merchant)
        username_id = merchant['username_id']

        username = await db['usernames'].find_one({"_id": username_id})
        if not username:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Username not found.")

        username = jsonable_encoder(username)
        merchant['username'] = username['username']

        return merchant

    except PyMongoError as e:
        # Handle MongoDB related errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get('/username/{username}', response_model=user_model.MerchantQueryResponseData)
async def get_merchant_by_username(username: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    # Use an aggregation pipeline to perform the entire operation in one query
    pipeline = [
        {
            "$match": {"username": username}
        },
        {
            "$lookup": {
                "from": "merchants",
                "localField": "user_id",
                "foreignField": "user_id",
                "as": "user_profile"
            }
        },
        {
            "$unwind": "$user_profile"
        },
        {
            "$lookup": {
                "from": "services",
                "localField": "user_id",
                "foreignField": "owner_id",
                "as": "user_profile.services"
            }
        },
    ]

    try:
        result = await db['usernames'].aggregate(pipeline).to_list(1)
        # username = await collections['usernames'].find_one({'username':username.lower()})
        # return username
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Username not found")
        if not result[0].get('user_profile'):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Merchant profile not found.")
        # return result
        services_list = []
        services = result[0].get('user_profile').get('services')
        for service in services:
            # service = jsonable_encoder(service)
            services_list.append(
                service_model.ServiceSnapshotResponse.model_validate(service))
            # print(merchant_models.Service(**service))
        # return services_list
        # profiles = result[0].get('user_profile').get('profiles')
        # return profiles
        # merchant_profile = None
        response = {
            'username': result[0].get('username'),
            'name': result[0].get('user_profile').get('name'),
            'profile': result[0].get('user_profile'),
            'services': services_list
        }

        # merchant_profile = profile

        # return merchant_profile
        # print(res)
        return response

    except Exception as e:
        raise e
    # HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{e}")


@router.post('/create', status_code=status.HTTP_201_CREATED, dependencies=[Depends(auth.implicit_scheme)], response_model=user_model.MerchantProfileData)
async def create_merchant_profile(payload: user_model.CreateMerchantData, user_profile: Auth0User = Security(auth.get_user), client: AsyncIOMotorClient = Depends(get_db_client), db_name: str = Depends(get_db_name)):

    payload = jsonable_encoder(payload)
    user_id = user_profile.id
    db = client[db_name]
    # Start a client session for the transaction
    session = await client.start_session()
    # async with session.start_transaction():
    # Try to Start the transaction
    try:
        async with session.start_transaction():
            # Check if a current user aleready has a merchant account.
            merchant = await db['merchants'].find_one({'user_id': user_id})
            if merchant:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                    detail="Merchant Profile Already Exists. Update Instead.")

            # Check if requested username is available
            username_available = await db['usernames'].find_one({'username': payload['username']})
            if username_available:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                    detail="Username already exists. Please try another one.")

            # Create new username object
            username_object = CreateUserName(
                username=payload["username"], user_auth0_id=user_profile.id)
            db_username_object = {
                "_id": str(username_object.id),
                "username": payload["username"],
                "user_id": user_profile.id,
            }

            # Insert the new username into the database
            new_username = await db['usernames'].insert_one(db_username_object)
            new_username_object = await db['usernames'].find_one({'_id': new_username.inserted_id})
            payload['username_id'] = str(new_username_object['_id'])

            # Prepare merchant data
            settings = get_default_notification_settings()
            schedule = get_default_schedule()
            new_merchant_data = user_model.MerchantDBStructure(
                **payload, user_id=user_id, settings=settings, schedule=schedule)
            new_merchant_data = jsonable_encoder(new_merchant_data)
            # return new_merchant_data
            new_merchant_data = user_model.MerchantDBInsert(
                id=str(payload["_id"]), **new_merchant_data)

            new_merchant_data = jsonable_encoder(new_merchant_data)

            # Insert the new merchant into the database
            new_merchant_profile = await db['merchants'].insert_one(new_merchant_data)

            # Retrieve and prepare the response data
            profile_with_merchant_details = await db['merchants'].find_one({'_id': new_merchant_profile.inserted_id})
            merchant_username_id = profile_with_merchant_details['username_id']
            username = await db['usernames'].find_one({"_id": merchant_username_id})
            username = jsonable_encoder(username)
            profile_with_merchant_details = jsonable_encoder(
                profile_with_merchant_details)
            profile_response = user_model.MerchantProfileData(
                **profile_with_merchant_details, username=username['username'])

            # Return the response
            return profile_response

    except pymongo.errors.InvalidOperation:
        # Log the error (optional, but recommended for debugging)
        logging.error(
            "A transaction is already in progress in this session.")
        await session.abort_transaction()

    except Exception as e:
        raise e

    finally:
        # End the session after the transaction is complete
        await session.end_session()


@router.put('/update/update_merchant_profile', status_code=status.HTTP_200_OK, dependencies=[Depends(auth.implicit_scheme)], response_model=user_model.MerchantProfileData)
async def update_merchant_profile(payload: user_model.UpdateMerchantData, user_profile: Auth0User = Security(auth.get_user), db: AsyncIOMotorDatabase = Depends(get_db)):

    payload = jsonable_encoder(payload)
    user_id = user_profile.id
    try:
        merchant = await db['merchants'].find_one({'user_id': user_id, })
        # print(user)
        if not merchant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Merchant profile does not exist. Please create one.")

        # ADD LOGIC TO UPDATE USERNAME HERE
        username = await db['usernames'].find_one({'username': payload['username']})
        if username:
            if username['user_id'] != user_id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                    detail="Username already exists. Please try another one.")

            if username['username'] != payload['username']:
                updated_username = await db['usernames'].update_one({'user_id': user_id}, {"$set": {"username": payload['username']}})
                if updated_username.matched_count == 0:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND, detail="Username record found")
                if updated_username.modified_count == 0:
                    raise HTTPException(
                        status_code=status.HTTP_304_NOT_MODIFIED, detail="Username not updated")
        if not username:
            updated_username = await db['usernames'].update_one({'user_id': user_id}, {"$set": {"username": payload['username']}})
            if updated_username.matched_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Username record found")
            if updated_username.modified_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_304_NOT_MODIFIED, detail="Username not updated")

        del payload['username']
        # Ensure user only updates their own profile
        updated_user = await db['merchants'].update_one({'user_id': user_id}, {"$set":  payload})
        # print("F")

        if updated_user.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

        if updated_user.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_304_NOT_MODIFIED, detail="Profile data not updated")

        if (merchant := await db['merchants'].find_one({'user_id': user_id})) is not None:
            merchant = jsonable_encoder(merchant)
            # print(user)
            merchant_username_id = merchant['username_id']
            username = await db['usernames'].find_one({"_id": merchant_username_id})
            username = jsonable_encoder(username)
            merchant['username'] = username['username']
            return merchant
            # return user

    except Exception as e:
        raise e


@router.put('/update/basic-info', status_code=status.HTTP_200_OK, dependencies=[Depends(auth.implicit_scheme)], response_model=user_model.MerchantProfileData)
async def update_merchant_basic_info(payload: user_model.MerchantBasicInfo, user_profile: Auth0User = Security(auth.get_user), db: AsyncIOMotorDatabase = Depends(get_db)):

    payload = jsonable_encoder(payload)
    user_id = user_profile.id
    try:
        merchant = await db['merchants'].find_one({'user_id': user_id})
        # print(user)
        if not merchant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Merchant profile does not exist. Please create one.")

        # ADD LOGIC TO UPDATE USERNAME HERE
        username = await db['usernames'].find_one({'username': payload['username']})
        if username:
            if username['user_id'] != user_id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                    detail="Username already exists. Please try another one.")

            if username['username'] != payload['username']:
                updated_username = await db['usernames'].update_one({'user_id': user_id}, {"$set": {"username": payload['username']}})
                if updated_username.matched_count == 0:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND, detail="Username record found")
                if updated_username.modified_count == 0:
                    raise HTTPException(
                        status_code=status.HTTP_304_NOT_MODIFIED, detail="Username not updated")
        if not username:
            updated_username = await db['usernames'].update_one({'user_id': user_id}, {"$set": {"username": payload['username']}})
            if updated_username.matched_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Username record found")
            if updated_username.modified_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_304_NOT_MODIFIED, detail="Username not updated")

        del payload['username']

        updated_user = await db['merchants'].update_one({'user_id': user_id}, {"$set":  payload})

        if updated_user.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

        if updated_user.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_304_NOT_MODIFIED, detail="Profile data not updated")

        if (merchant := await db['merchants'].find_one({'user_id': user_id})) is not None:
            merchant = jsonable_encoder(merchant)
            merchant_username_id = merchant['username_id']
            username = await db['usernames'].find_one({"_id": merchant_username_id})
            username = jsonable_encoder(username)
            merchant['username'] = username['username']
            return merchant

    except Exception as e:
        raise e


@router.put('/update/location-info', status_code=status.HTTP_200_OK, dependencies=[Depends(auth.implicit_scheme)], response_model=user_model.MerchantProfileData)
async def update_merchant_location_info(payload: user_model.Location, user_profile: Auth0User = Security(auth.get_user), db: AsyncIOMotorDatabase = Depends(get_db)):
    payload = jsonable_encoder(payload)
    user_id = user_profile.id
    try:
        merchant = await db['merchants'].find_one({'user_id': user_id})
        # print(user)
        if not merchant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Merchant profile does not exist. Please create one.")

        updated_user = await db['merchants'].update_one({'user_id': user_id}, {"$set": {"location": payload}})

        if updated_user.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

        if updated_user.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_304_NOT_MODIFIED, detail="Profile data not updated")

        if (merchant := await db['merchants'].find_one({'user_id': user_id})) is not None:
            merchant = jsonable_encoder(merchant)
            merchant_username_id = merchant['username_id']
            username = await db['usernames'].find_one({"_id": merchant_username_id})
            username = jsonable_encoder(username)
            merchant['username'] = username['username']
            return merchant

    except Exception as e:
        raise e


def validate_schedule(schedule: user_model.Schedule):
    def is_time_after(time1: time, time2: time) -> bool:
        """Check if time1 is after time2."""
        return time1 is not None and time2 is not None and time1 > time2

    def is_time_within(time: time, start: time, end: time) -> bool:
        """Check if time t is within the start and end time."""
        return start <= time <= end

    for day, daily_schedule in schedule.daily_schedule.model_dump().items():
        # print(day)
        operating_hours = daily_schedule.get('operating_hours')
        blocked_hours = daily_schedule.get('blocked_hours')

        # Validate operating hours
        if operating_hours.get('start_time') and operating_hours.get('end_time'):
            if is_time_after(operating_hours.get('start_time'), operating_hours.get('end_time')):
                raise ValueError(
                    f"Invalid operating hours on \'{day}\': end_time must be after start_time.")

        # Validate blocked hours
        for block in blocked_hours:
            if block.get('start_time') and block.get('end_time'):
                if is_time_after(block.get('start_time'), block.get('end_time')):
                    raise ValueError(
                        f"Invalid blocked hours on \'{day}\': end_time must be after start_time.")

                if not is_time_within(block.get('start_time'), operating_hours.get('start_time'), operating_hours.get('end_time')) or \
                        not is_time_within(block.get('end_time'), operating_hours.get('start_time'), operating_hours.get('end_time')):
                    raise ValueError(
                        f"Blocked hours on \'{day}\' must fall within operating hours.")

    return True


@router.put('/update/availability')
async def update_availability(payload: user_model.Schedule, user_profile: Auth0User = Security(auth.get_user), db: AsyncIOMotorDatabase = Depends(get_db)):
    user_id = user_profile.id
    try:
        if validate_schedule(user_model.Schedule.model_validate(payload)):

            merchant = await db['merchants'].find_one({'user_id': user_id})
            if not merchant:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="Merchant profile does not exist. Please create one.")
            payload = jsonable_encoder(payload)
            updated_user = await db['merchants'].update_one({'user_id': user_id}, {"$set": {"schedule": payload}})

        if updated_user.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

        if updated_user.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_304_NOT_MODIFIED, detail="Profile data not updated")

        if (merchant := await db['merchants'].find_one({'user_id': user_id})) is not None:
            merchant = jsonable_encoder(merchant)
            # print(user)
            schedule = merchant.get('schedule')
            return schedule

    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))

    except HTTPException as http_exc:
        raise http_exc


@router.delete('/delete', status_code=status.HTTP_200_OK, dependencies=[Depends(auth.implicit_scheme)])
async def delete_merchant_profile(user_profile: Auth0User = Depends(auth.get_user), db: AsyncIOMotorDatabase = Depends(get_db)):
    user_id = user_profile.id

    try:
        merchant = await db['merchants'].find_one({'user_id': user_id})

        if not merchant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Merchant profile not found.")

        # Retrieve username_id from the merchant profile
        username_id = merchant.get('username_id')
        if not username_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Associated username reference not found.")

        # Delete the merchant profile
        await db['merchants'].delete_one({'user_id': user_id})

        # Delete the associated username
        await db['usernames'].delete_one({'_id': username_id})

        return {"detail": "Merchant profile and associated username deleted successfully."}

    except HTTPException as http_err:
        print(http_err)
        raise http_err
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))


@router.put('/update/intro-video-url', status_code=status.HTTP_200_OK, dependencies=[Depends(auth.implicit_scheme)], response_model=user_model.MerchantProfileData)
async def update_intro_video_url(payload: user_model.UpdateIntroVideoURL, user_profile: Auth0User = Security(auth.get_user), db: AsyncIOMotorDatabase = Depends(get_db)):
    user_id = user_profile.id
    try:
        merchant = await db['merchants'].find_one({'user_id': user_id})
        if not merchant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Merchant profile does not exist. Please create one.")

        updated_user = await db['merchants'].update_one({'user_id': user_id}, {"$set": {"intro_video_url": payload.intro_video_url}})

        if updated_user.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

        if updated_user.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_304_NOT_MODIFIED, detail="Profile data not updated")

        if (merchant := await db['merchants'].find_one({'user_id': user_id})) is not None:
            merchant = jsonable_encoder(merchant)
            merchant_username_id = merchant['username_id']
            username = await db['usernames'].find_one({"_id": merchant_username_id})
            username = jsonable_encoder(username)
            merchant['username'] = username['username']
            return merchant

    except Exception as e:
        raise e


@router.put('/update/profile-picture-url', status_code=status.HTTP_200_OK, dependencies=[Depends(auth.implicit_scheme)], response_model=user_model.MerchantProfileData)
async def update_profile_picture_url(payload: user_model.UpdateProfilePictureURL, user_profile: Auth0User = Security(auth.get_user), db: AsyncIOMotorDatabase = Depends(get_db)):
    user_id = user_profile.id
    try:
        merchant = await db['merchants'].find_one({'user_id': user_id})
        if not merchant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Merchant profile does not exist. Please create one.")

        updated_user = await db['merchants'].update_one({'user_id': user_id}, {"$set": {"profile_picture_url": payload.profile_picture_url}})

        if updated_user.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

        if updated_user.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_304_NOT_MODIFIED, detail="Profile data not updated")

        if (merchant := await db['merchants'].find_one({'user_id': user_id})) is not None:
            merchant = jsonable_encoder(merchant)
            merchant_username_id = merchant['username_id']
            username = await db['usernames'].find_one({"_id": merchant_username_id})
            username = jsonable_encoder(username)
            merchant['username'] = username['username']
            return merchant

    except Exception as e:
        raise e


# ================= STILL NEEDED ================= #

# UPDATE AVAILABILITY SCHEDULE
# PUBLISH MERCHANT
# UNPUBLISH MERCHANT
# GET ALL MERCHANTS (HOME PAGE CARD_DATA)
# GET MERCHANT BY USERNAME

# ===================== ENDS ===================== #
