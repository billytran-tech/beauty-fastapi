from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, ConfigDict
from app.config.config import settings
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.auth.auth import Auth0, Auth0User
from app.config.database.database import get_db
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


@router.get('/account/id')
async def authorize_user(user_profile: Auth0User = Depends(auth.get_user), db: AsyncIOMotorDatabase = Depends(get_db)):
    user_id = user_profile.id
    merchant = await db['merchants'].find_one({'user_id': user_id})

    return merchant.get('payments_account').get('account_id')


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
