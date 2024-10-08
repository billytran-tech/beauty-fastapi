from fastapi import HTTPException, status
from pydantic import BaseModel, ConfigDict
import stripe
from stripe import StripeError
from app.auth.auth import Auth0User
from app.config.config import settings
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.schema.object_models.v0 import booking_model

stripe.api_key = settings.STRIPE_SECRET_KEY
payment_return_url = settings.PAYMENT_RETURN_URL


class PaymentsAccount(BaseModel):
    provider: str
    account_id: str

    model_config = ConfigDict(populate_by_name=True,
                              arbitrary_types_allowed=True)


async def create_stripe_connected_account(user_profile: Auth0User, email: str, country_code: str, db: AsyncIOMotorDatabase):
    """
    Create a Stripe Connected Account for the given user.
    """
    try:
        user_id = user_profile.id
        account = stripe.Account.create(
            type='express',
            country=country_code,
            email=email,
            capabilities={
                'card_payments': {'requested': True},
                'transfers': {'requested': True},
            },
        )

        payments_account = {
            'provider': 'stripe',
            'account_id': account.id
        }

        updated_merchant = await db['merchants'].update_one({'user_id': user_id}, {"$set": {"payments_account": payments_account}})
        if updated_merchant.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Merchant Account Record found")
        if updated_merchant.modified_count == 0:
            raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED)

        return account.id
    except StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException as http_exc:
        raise http_exc


async def get_stripe_account_id(user_profile: Auth0User, db: AsyncIOMotorDatabase):
    """
    Get the Stripe account ID for a user with a connected account.
    """
    user_id = user_profile.id
    merchant = await db['merchants'].find_one({'user_id': user_id})

    if (merchant.get('payments_account').get('provider') == 'stripe'):
        return merchant.get('payments_account').get('account_id')
    return


def check_stripe_onboarding_status(account_id: str):
    """
    Check the onboarding status of a user's Stripe account.
    """
    try:
        account = stripe.Account.retrieve(account_id)
        return account.details_submitted
    except StripeError as e:
        print(f"Error checking Stripe onboarding status: {str(e)}")
        return False


def generate_stripe_login_link(account_id: str):
    """
    Generate a login link for the user to access their Stripe dashboard.
    """
    try:
        login_link = stripe.Account.create_login_link(account_id)
        return login_link.url
    except StripeError as e:
        print(f"Error generating Stripe login link: {str(e)}")
        return None


def fetch_stripe_account_balance(account_id: str):
    """
    Fetch the balance of a user's Stripe connected account.
    """
    try:
        balance = stripe.Balance.retrieve(stripe_account=account_id)
        return balance
    except StripeError as e:
        print(f"Error fetching Stripe account balance: {str(e)}")
        return None


def get_line_items(booking: booking_model.BookingFullModel):
    line_items = [
        {
            'price_data': {
                'currency': booking.service.price.currency.code.lower(),
                'product_data': {
                    'name': booking.service.service_name,
                    'description': booking.service.description,
                    'images': booking.service.images,
                },
                'unit_amount': 500
            },
            'quantity': 1
        }
    ]
    return line_items


def create_checkout_session(booking: booking_model.BookingFullModel, email: str):
    """
    Create a Stripe Checkout session for the given user and items.

    :param account_id: The Stripe account ID of the user
    :param items: A list of dictionaries containing 'price_data' and 'quantity' for each item
    :param success_url: The URL to redirect to after successful payment
    :param cancel_url: The URL to redirect to if the user cancels the payment
    :return: The created Checkout session object or None if there's an error
    """
    try:
        checkout_session = stripe.checkout.Session.create(
            ui_mode='embedded',
            payment_method_types=['card'],
            customer_email=email,
            line_items=get_line_items(booking),
            mode='payment',
            return_url=payment_return_url,
            metadata={
                'booking_id': booking.id
            },
            payment_intent_data={
                "metadata": {
                    "booking_id": booking.id,
                }
            },
        )
        return checkout_session.client_secret
    except StripeError as e:
        print(f"Error creating Checkout session: {str(e)}")
        return None


def get_checkout_session_status(id: str):
    session = stripe.checkout.Session.retrieve(id)
    return {
        'status': session.status,
        'customer_email': session.customer_details.email
    }
