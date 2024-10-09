import datetime as super_datetime
from app.schema.object_models.v0.schedule_model import Schedule
from datetime import datetime, timedelta
from typing import Annotated, List
from fastapi import Depends, FastAPI, HTTPException, APIRouter, Security, status, Query, Request
from fastapi.encoders import jsonable_encoder
from datetime import date, datetime, timedelta
from app.schema.object_models.v0 import booking_model, service_model, user_model
from app.config.database.database import get_db, get_db_client, get_db_name
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClient
from app.schema.enums.enums import BookingStatusEnum, PaymentStatusEnum
from app.config.config import settings
from app.auth.auth import Auth0, Auth0User
from app.services.payments.stripe import create_checkout_session

router = APIRouter(
    prefix="/api/bookings",
    tags=["Bookings"],
)

auth0_domain = settings.AUTH0_DOMAIN
auth0_api_audience = settings.AUTH0_API_AUDIENCE
auth = Auth0(domain=auth0_domain, api_audience=auth0_api_audience, scopes={})


def calculate_possible_start_times(schedule: Schedule, appointment_duration_minutes: int, ref_date: date, bookings_list: List[booking_model.BookingFullModel]):
    possible_start_times = {}
    schedule = jsonable_encoder(schedule.daily_schedule)
    # return schedule

    for i in range(7):
        current_date = ref_date + timedelta(days=i)
        possible_start_times[current_date] = []

        duration_minutes = appointment_duration_minutes
        day_of_week = current_date.strftime('%A').lower()

        day_schedule = schedule.get(day_of_week)
        if not day_schedule or not day_schedule.get('is_available'):
            possible_start_times[current_date] = []
            continue
        operating_hours = day_schedule.get('operating_hours')

        start_time_only = operating_hours.get(
            'start_time').replace('Z', '+00:00')
        end_time_only = operating_hours.get('end_time').replace('Z', '+00:00')

        start_time = datetime.strptime(
            f'{current_date}T{start_time_only}', '%Y-%m-%dT%H:%M:%S%z')
        end_time = datetime.strptime(
            f'{current_date}T{end_time_only}', '%Y-%m-%dT%H:%M:%S%z')

        blocked_hours = []
        for block in day_schedule.get('blocked_hours'):
            blocked_start_time_only = block.get(
                'start_time').replace('Z', '+00:00')
            blocked_end_time_only = block.get(
                'end_time').replace('Z', '+00:00')
            blocked_start = datetime.strptime(
                f'{current_date}T{blocked_start_time_only}', '%Y-%m-%dT%H:%M:%S%z')
            blocked_end = datetime.strptime(
                f'{current_date}T{blocked_end_time_only}', '%Y-%m-%dT%H:%M:%S%z')
            blocked_hours.append((blocked_start, blocked_end))

        interval = timedelta(minutes=30)
        appointment_duration = timedelta(minutes=duration_minutes)

        current_time = start_time

        while current_time + appointment_duration <= end_time:
            is_blocked = any(block_start <= current_time <
                             block_end for block_start, block_end, in blocked_hours)
            if not is_blocked:
                overlap = False
                for booking in bookings_list:
                    booking = booking_model.BookingFullModel.model_validate(
                        booking)
                    if (booking.booking_status == BookingStatusEnum.CANCELLED):

                        continue
                    appt_start = booking.appointment_date.start_time
                    appt_end = booking.appointment_date.end_time
                    if (current_time < appt_end and (current_time + appointment_duration) > appt_start):
                        overlap = True
                if not overlap:
                    possible_start_times[current_date].append(
                        current_time.timetz())
            current_time += interval

    return possible_start_times


@router.get('/availability/{username}/{starting_date}/{duration_minutes}')
async def get_availability_for_next_7_days(username: str, starting_date: date, duration_minutes: int, db: AsyncIOMotorDatabase = Depends(get_db)):

    bookings = []
    username_object = await db['usernames'].find_one({'username': username})

    if not username_object:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='User not found')

    user_id = jsonable_encoder(username_object).get('user_id')
    merchant = await db['merchants'].find_one({'user_id': user_id})
    # merchant = jsonable_encoder(merchant)
    # return merchant
    schedule = Schedule.model_validate(merchant.get('schedule'))

    merchant = user_model.MerchantModelForComparison.model_validate(merchant)

    # return schedule
    bookings = await db['bookings'].find({'merchant.id': merchant.id}).to_list(length=None)
    # bookings_list = []
    # for booking in bookings:
    #     booking = booking_model.BookingFullModel.model_validate(booking)
    #     bookings_list.append(booking)
    # bookings = jsonable_encoder(bookings)
    # return bookings
    available_slots = calculate_possible_start_times(
        schedule, duration_minutes, starting_date, bookings)
    return available_slots


@router.get('/customer/my-bookings')
async def get_my_bookings_as_customer(
    user_profile: Auth0User = Security(auth.get_user),
    page: Annotated[int, Query(description="Page number")] = 1,
    per_page: Annotated[int, Query(description="Items per page")] = 10,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    user_id = user_profile.id
    if page < 1 or per_page < 1:
        raise HTTPException(
            status_code=400, detail="Invalid page or per_page values")

    # Calculate the number of documents to skip
    skip = (page - 1) * per_page

    # Query MongoDB using skip and limit
    bookings = await db['bookings'].find({"customer.id": user_id}).skip(skip).limit(per_page).to_list(length=None)

    return bookings


@router.get('/merchant/my-bookings')
async def get_my_bookings_as_merchant(
    user_profile: Auth0User = Security(auth.get_user),
    page: Annotated[int, Query(description="Page number")] = 1,
    per_page: Annotated[int, Query(description="Items per page")] = 10,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    user_id = user_profile.id
    # raise HTTPException(status_code=501, detail="Not implemented")
    if page < 1 or per_page < 1:
        raise HTTPException(
            status_code=400, detail="Invalid page or per_page values")

    # Calculate the number of documents to skip
    skip = (page - 1) * per_page

    # Query MongoDB using skip and limit
    bookings = await db['bookings'].find({"merchant.id": user_id}).skip(skip).limit(per_page).to_list(length=None)

    return bookings


async def check_overlap(appointment_date: date, service_duration_minutes: int, merchant_id: str, db: AsyncIOMotorDatabase):
    overlap_exists = False
    start_time = appointment_date
    end_time = start_time + timedelta(minutes=service_duration_minutes)

    bookings = []
    async for item in db['bookings'].find({"merchant.id": merchant_id}):
        bookings.append(item)

    # calculate_possible_start_times(schedule, service.duration_minutes, payload.appointment_date.date.date(),)

    # day_of_week = appointment_date.strftime('%A').lower()

    # print(day_of_week)

    # calculate_possible_start_times
    for existing_appointment in bookings:
        existing_appointment = booking_model.BookingFullModel.model_validate(
            existing_appointment)
        if (existing_appointment.booking_status == BookingStatusEnum.CANCELLED):
            continue
        existing_start_time = existing_appointment.appointment_date.start_time
        existing_end_time = existing_appointment.appointment_date.end_time
        if (start_time < existing_end_time) and (end_time > existing_start_time):
            overlap_exists = True

    return overlap_exists


@router.post('/create')
async def create_new_booking(payload: booking_model.CreateBooking, user_profile: Auth0User = Depends(auth.get_user), db: AsyncIOMotorDatabase = Depends(get_db)):
    # Get Service + Duration then calculate end time
    user_id = user_profile.id
    # return payload
    customer = await db['customers'].find_one({'user_id': user_id})

    customer_info = ''

    if customer:
        customer_info = booking_model.ClientObject.model_validate(customer)
    else:
        customer_info = {
            'id': user_profile.id,
            'name': user_profile.email,
            'profile_picture_url': None,
            'user_id': user_profile.id

        }
        customer_info = booking_model.ClientObject.model_validate(
            customer_info)

    service = await db['services'].find_one({'_id': payload.service_id})
    service = service_model.ServiceDBObject.model_validate(service)
    # return service
    merchant = await db['merchants'].find_one({'user_id': service.owner_id})
    merchant_info = booking_model.MerchantObject.model_validate(merchant)
    merchant = user_model.MerchantDBInsert.model_validate(merchant)
    # return service
    service = booking_model.ServiceObject.model_validate(
        jsonable_encoder(service))

    appointment_date = {
        'start_time': payload.appointment_date.date,
        'end_time': payload.appointment_date.date + timedelta(minutes=service.duration_minutes)
    }
    appointment_date = booking_model.AppointmentDate.model_validate(
        appointment_date)

    booking_info = {
        '_id': str(payload.id),
        'customer': customer_info.model_dump(),
        'merchant': merchant_info.model_dump(),
        'appointment_date': appointment_date.model_dump(),
        'service': service,
        'booking_status': 'pending',
        'payment_status': 'pending',
        'appointment_location': merchant.location,
    }
    # return booking_info
    booking_info = booking_model.BookingFullModel.model_validate(booking_info)

    if (await check_overlap(payload.appointment_date.date, service.duration_minutes, merchant.id, db)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail='Merchant Not Available. Booking overlaps with an existing booking.')

    booking_info = jsonable_encoder(booking_info)
    booking = await db['bookings'].insert_one(booking_info)

    new_booking = await db['bookings'].find_one({'_id': booking.inserted_id})
    new_booking = booking_model.BookingFullModel.model_validate(new_booking)
    checkout_client_secret = create_checkout_session(
        new_booking, user_profile.email)
    return {
        'new_booking': new_booking,
        'client_secret': checkout_client_secret
    }


# REQUEST RESCHEDULE (POST)
@router.post('/request-reschedule/{booking_id}')
async def request_reschedule(booking_id: str, user_profile: Auth0User = Depends(auth.get_user), db: AsyncIOMotorDatabase = Depends(get_db)):
    user_id = user_profile.id

    booking = await db['bookings'].find_one({'_id': booking_id})
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Booking Not Found')
    booking = booking_model.BookingFullModel.model_validate(booking)

    merchant = await db['merchants'].find_one({'user_id': user_id})
    if not merchant:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='You are not authorized to perform this action.')
    merchant = user_model.MerchantModelForComparison.model_validate(merchant)

    if not (merchant.id == booking.merchant.id):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='You are not authorized to perform this action.')

    new_booking_status = BookingStatusEnum.RESCHEDULE_PENDING
    # TODO: Should Automatically Cancel After Time Threshold

    booking_update = await db['bookings'].update_one({'_id': booking_id}, {'$set': {'booking_status': new_booking_status.value}})

    if booking_update.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Booking Not Found.")
    if booking_update.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED)

    updated_booking = await db['bookings'].find_one({'_id': booking_id})
    updated_booking = booking_model.BookingFullModel.model_validate(
        updated_booking)
    return updated_booking


@router.get('/{booking_id}')
async def get_booking_by_id(booking_id: str, user_profile: Auth0User = Depends(auth.get_user), db: AsyncIOMotorDatabase = Depends(get_db)):

    booking = await db['bookings'].find_one({'_id': booking_id})
    booking = booking_model.BookingFullModel.model_validate(booking)

    merchant = await db['merchants'].find_one({'_id': booking.merchant.id})
    # if not merchant:
    merchant = user_model.MerchantModelForComparison.model_validate(merchant)
    # return merchant.id

    if not ((merchant.user_id == user_profile.id) or (booking.customer.id == user_profile.id)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized.')

    return booking


@router.put('/reschedule/{booking_id}')
async def reschedule_booking(payload: booking_model.AppointmentStartDate, booking_id: str, user_profile: Auth0User = Depends(auth.get_user), db: AsyncIOMotorDatabase = Depends(get_db)):

    booking = booking = await db['bookings'].find_one({'_id': booking_id})
    booking = booking_model.BookingFullModel.model_validate(booking)

    if not (booking.customer.id == user_profile.id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized.')

    if (payload.date < datetime.now(super_datetime.UTC)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Appointment date is in the past")

    if (await check_overlap(payload.date, booking.service.duration_minutes, booking.merchant.id, db)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail='Merchant Not Available. Booking overlaps with an existing booking.')

    new_appointment_date = {
        'start_time': payload.date,
        'end_time': payload.date + timedelta(minutes=booking.service.duration_minutes)
    }
    new_appointment_date = booking_model.AppointmentDate.model_validate(
        new_appointment_date)

    booking_status = booking.booking_status
    if (booking.booking_status == BookingStatusEnum.RESCHEDULE_PENDING):
        booking_status = BookingStatusEnum.PENDING
    if ((booking.booking_status == BookingStatusEnum.PENDING) and (booking.payment_status == PaymentStatusEnum.SUCCESS)):
        booking_status == BookingStatusEnum.CONFIRMED

    # return new_appointment_date
    booking_update = await db['bookings'].update_one({'_id': booking_id}, {'$set': {'appointment_date': jsonable_encoder(new_appointment_date), 'booking_status': booking_status.value}})

    if booking_update.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Booking Not Found.")
    if booking_update.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED)

    updated_booking = await db['bookings'].find_one({'_id': booking_id})
    updated_booking = booking_model.BookingFullModel.model_validate(
        updated_booking)
    return updated_booking


@router.put('/cancel/{booking_id}')
async def cancel_booking(booking_id: str, user_profile: Auth0User = Depends(auth.get_user), db: AsyncIOMotorDatabase = Depends(get_db)):

    booking = await db['bookings'].find_one({'_id': booking_id})
    booking = booking_model.BookingFullModel.model_validate(booking)

    merchant = await db['merchants'].find_one({'_id': booking.merchant.id})
    # if not merchant:
    merchant = user_model.MerchantModelForComparison.model_validate(merchant)
    # return merchant.id

    if not ((merchant.user_id == user_profile.id) or (booking.customer.id == user_profile.id)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized.')

    payment_status = booking.payment_status
    if (payment_status == PaymentStatusEnum.SUCCESS):
        payment_status = PaymentStatusEnum.REFUND_PENDING
    if (payment_status == PaymentStatusEnum.PENDING):
        payment_status = PaymentStatusEnum.CANCELLED

    new_booking_status = BookingStatusEnum.CANCELLED

    booking_update = await db['bookings'].update_one({'_id': booking_id}, {'$set': {'booking_status': new_booking_status.value, 'payment_status': payment_status}})

    if booking_update.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Booking Not Found.")
    if booking_update.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED)

    updated_booking = await db['bookings'].find_one({'_id': booking_id})
    updated_booking = booking_model.BookingFullModel.model_validate(
        updated_booking)
    return updated_booking
