from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
import stripe
from app.config.database.database import get_db
from app.schema.enums.enums import BookingStatusEnum, PaymentStatusEnum, PaymentGatewayEnum
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.config.config import settings

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])

endpoint_secret = settings.STRIPE_WEBHOOK_SECRET


@router.post("/stripe")
async def stripe_webhook(request: Request, db: AsyncIOMotorDatabase = Depends(get_db)):
    """
    Handle Stripe webhook events.

    Args:
        request (Request): The incoming webhook request.

    Returns:
        dict: A dictionary indicating the status of the webhook processing.
    """
    # GET THE RAW PAYLOAD AND STRIPE-SIGNATURE HEADER FROM THE INCOMING REQUEST
    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature")
    event = None
    try:
        # VERIFY THE SIGNATURE AND PARSE THE WEBHOOK EVENT
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # return HTTPException(status_code=400, detail=str(e))
        raise e
    except stripe.SignatureVerificationError as e:
        #         # Invalid signature
        raise e
    # print('EVENT TYPE: ' + event["type"]+"\n")
    # if event["type"] == "payment_intent.created":
    #     payment_intent = event['data']
    #     payment_intent = payment_intent['object']
    #     payment_intent_id = payment_intent['id']
    #     booking_id = payment_intent['metadata'].get('booking_id')
    #     booking_info_to_update = {
    #         'payment': PaymentStatusEnum.PENDING.value,
    #     }
    #     # transaction = {
    #     #     'payment_gateway': PaymentGatewayEnum.STRIPE.value,
    #     #     'booking_id': booking_id,
    #     #     'payment_intent': payment_intent,
    #     # }
    #     # await db['transactions'].insert_one(transaction)
    #     await db['bookings'].update_one({"_id": booking_id}, {"$set": booking_info_to_update})

    # CHECK IF THE EVENT TYPE IS PAYMENT_INTENT.SUCCEEDED
    if event["type"] == "payment_intent.succeeded":
        payment_intent = event['data']
        payment_intent = payment_intent['object']
        payment_intent = jsonable_encoder(payment_intent)
        # UPDATE APPOINTMENT AND TRANSACTION WITH PAYMENT INFORMATION
        booking_id = payment_intent['metadata'].get('booking_id')

        transaction = {
            'payment_gateway': PaymentGatewayEnum.STRIPE.value,
            'booking_id': booking_id,
            'payment_intent': payment_intent,
        }
        # transaction = jsonable_encoder(transaction)

        booking_info_to_update = {
            'payment_status': PaymentStatusEnum.SUCCESS.value,
            'booking_status': BookingStatusEnum.CONFIRMED.value,
        }
        # print('==========START==========')
        # print(booking_info_to_update)
        # print('==========END==========')
        await db['transactions'].insert_one(transaction)

        await db['bookings'].update_one({"_id": booking_id}, {"$set": booking_info_to_update})
        # booking_update = await db['bookings'].update_one({'_id': booking_id}, {'$set': {'payment': 'success123'}})
        # # updated_booking = z
        # if booking_update.matched_count == 0:
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND, detail="Booking Not Found.")
        # if booking_update.modified_count == 0:
        #     raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED)

    elif event["type"] == "payment_intent.failed":
        payment_intent = event['data']
        payment_intent = payment_intent['object']
        # payment_intent_id = payment_intent['id']
        booking_id = payment_intent['metadata'].get('booking_id')
        transaction = {
            'payment_gateway': PaymentGatewayEnum.STRIPE.value,
            'booking_id': booking_id,
            'payment_intent': payment_intent
        }
        booking_info_to_update = {
            'payment': PaymentStatusEnum.FAILED.value,
        }
        await db['transactions'].insert_one(transaction)
        await db['bookings'].update_one({"_id": booking_id}, {"$set": booking_info_to_update})

    return {"status": "success"}
