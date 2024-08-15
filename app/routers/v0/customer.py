from fastapi import APIRouter, status, Depends, HTTPException, Security
from fastapi.encoders import jsonable_encoder
from pydantic_core import ValidationError
from app.config.config import settings
from app.helpers.default_user_data import get_default_notification_settings
from app.schema.object_models.v0 import user_model
from app.config.database.database import get_db
from app.auth.auth import Auth0, Auth0User
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter(
    prefix='/api/customer',
    tags=['Customer Profile']
)

auth0_domain = settings.AUTH0_DOMAIN
auth0_api_audience = settings.AUTH0_API_AUDIENCE
auth = Auth0(domain=auth0_domain, api_audience=auth0_api_audience, scopes={})


async def get_customer_profile(user_id: str, db: AsyncIOMotorDatabase):
    customer = await db['customers'].find_one({'user_id': user_id})
    return customer


@router.get("/get-my-profile", status_code=status.HTTP_200_OK, response_model=user_model.CustomerDataResponse, dependencies=[Depends(auth.implicit_scheme)])
async def get_my_customer_profile(user_profile: Auth0User = Depends(auth.get_user), db: AsyncIOMotorDatabase = Depends(get_db)):
    try:
        if (customer := await get_customer_profile(user_profile.id, db)):
            return customer
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Customer profile does not exist. Please create one.")

    except HTTPException as http_err:
        raise http_err

    except Exception as e:
        raise e


@router.post('/create', status_code=status.HTTP_201_CREATED, response_model=user_model.CustomerDataResponse, dependencies=[Depends(auth.implicit_scheme)])
async def create_customer_profile(payload: user_model.CreateCustomer, user_profile: Auth0User = Security(auth.get_user), db: AsyncIOMotorDatabase = Depends(get_db)):

    try:
        user_id = user_profile.id

        if (await get_customer_profile(user_id, db)):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="Customer profile already exists. Try to update instead.")

        payload = jsonable_encoder(payload)
        new_customer = user_model.InsertDBCustomer(
            **payload, settings=get_default_notification_settings(), user_id=user_id)

        db_customer = await db['customers'].insert_one(jsonable_encoder(new_customer))
        new_db_customer = await db['customers'].find_one({'_id': db_customer.inserted_id})

        return new_db_customer

    except HTTPException as http_err:
        raise http_err

    except ValidationError as ve:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=ve.errors())
    except Exception as e:
        raise e


@router.put('/update/customer-profile', status_code=status.HTTP_200_OK, response_model=user_model.CustomerDataResponse, dependencies=[Depends(auth.implicit_scheme)])
async def update_customer_profile(payload: user_model.UpdateCustomerData, user_profile: Auth0User = Security(auth.get_user), db: AsyncIOMotorDatabase = Depends(get_db)):

    try:
        user_id = user_profile.id

        # Check if the customer profile exists
        existing_user = await db['customers'].find_one({'user_id': user_id})
        if not existing_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Customer Profile doesn't exist. Please create one instead.")

        # Ensure the user only updates their own profile
        updated_user = await db['customers'].update_one({'user_id': user_id}, {"$set": jsonable_encoder(payload)})

        if updated_user.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

        if updated_user.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_304_NOT_MODIFIED, detail="Profile data not updated")

        # Retrieve and return the updated customer profile
        user = await db['customers'].find_one({'user_id': user_id})
        return user

    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to update customer profile")


@router.delete('/delete', status_code=status.HTTP_200_OK, dependencies=[Depends(auth.implicit_scheme)])
async def delete_customer_profile(user_profile: Auth0User = Security(auth.get_user), db: AsyncIOMotorDatabase = Depends(get_db)):
    user_id = user_profile.id

    try:
        customer = await db['customers'].find_one({'user_id': user_id})

        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Customer profile not found.")

        # Delete the customer profile
        await db['customers'].delete_one({'user_id': user_id})

        return {"detail": "Customer profile deleted successfully."}

    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))
