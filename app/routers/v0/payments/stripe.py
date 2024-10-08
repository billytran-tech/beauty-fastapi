from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, ConfigDict
from app.config.config import settings
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.auth.auth import Auth0, Auth0User
from app.schema.object_models.v0 import booking_model
from app.config.database.database import get_db
from app.services.payments.stripe import create_checkout_session, get_checkout_session_status
# from app.services.payments.stripe import get_stripe_account_id

router = APIRouter(
    prefix='/api/stripe',
    tags=['Stripe Integration Handling'],
)

auth0_domain = settings.AUTH0_DOMAIN
auth0_api_audience = settings.AUTH0_API_AUDIENCE
auth = Auth0(domain=auth0_domain, api_audience=auth0_api_audience, scopes={})


class PaymentsAccount(BaseModel):
    provider: str
    account_id: str

    model_config = ConfigDict(populate_by_name=True,
                              arbitrary_types_allowed=True)


@router.get('/session_status/{session_id}')
def get_session_status(session_id: str):
    return get_checkout_session_status(session_id)


@router.get('/account/id')
async def authorize_user(user_profile: Auth0User = Depends(auth.get_user), db: AsyncIOMotorDatabase = Depends(get_db)):
    user_id = user_profile.id
    merchant = await db['merchants'].find_one({'user_id': user_id})

    if (merchant.get('payments_account')):
        return merchant.get('payments_account').get('account_id')

    return


@router.put('/update/account/id')
async def set_merchant_stripe_account_id(payload: PaymentsAccount, user_profile: Auth0User = Depends(auth.get_user), db: AsyncIOMotorDatabase = Depends(get_db)):
    user_id = user_profile.id
    merchant = await db['merchants'].find_one({'user_id': user_id})
    if merchant.get('payments_account'):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail='Payments Account Already Setup')

    payments_account = {
        'provider': 'stripe',
        'account_id': payload.account_id
    }

    updated_merchant = await db['merchants'].update_one({'user_id': user_id}, {"$set": {"payments_account": payments_account}})
    if updated_merchant.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Merchant Account Record found")
    if updated_merchant.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED)

    return {'message': 'Account updated successfully'}


@router.get('/checkout_session/{booking_id}')
async def get_checkout_session(booking_id: str, user_profile: Auth0User = Depends(auth.get_user), db: AsyncIOMotorDatabase = Depends(get_db)):
    booking = await db['bookings'].find_one({'_id': booking_id})
    booking = booking_model.BookingFullModel.model_validate(booking)
    client_secret = create_checkout_session(booking, user_profile.email)
    return {
        'client_secret': client_secret
    }
