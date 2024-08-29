from app.schema.object_models.v0.schedule_model import *


def get_default_notification_settings():
    return {
        "notification_preferences": {
            "BookingChanges": {
                "sms": True,
                "whatsapp": False,
                "email": True
            },
            "BookingReminders": {
                "sms": True,
                "whatsapp": False,
                "email": True
            },
            "SuavUpdates": {
                "sms": False,
                "whatsapp": False,
                "email": True
            },
            "SecuritySettings": {
                "sms": True,
                "whatsapp": False,
                "email": True
            },
        }
    }


def get_default_schedule():
    return {
        "preffered_timezone": "",
        "daily_schedule": {
            "monday": {
                "is_available": False,
                "operating_hours": {
                    "start_time": None,
                    "end_time": None
                },
                "blocked_hours": []
            },
            "tuesday": {
                "is_available": False,
                "operating_hours": {
                    "start_time": None,
                    "end_time": None
                },
                "blocked_hours": []
            },
            "wednesday": {
                "is_available": False,
                "operating_hours": {
                    "start_time": None,
                    "end_time": None
                },
                "blocked_hours": []
            },
            "thursday": {
                "is_available": False,
                "operating_hours": {
                    "start_time": None,
                    "end_time": None
                },
                "blocked_hours": []
            },
            "friday": {
                "is_available": False,
                "operating_hours": {
                    "start_time": None,
                    "end_time": None
                },
                "blocked_hours": []
            },
            "saturday": {
                "is_available": False,
                "operating_hours": {
                    "start_time": None,
                    "end_time": None
                },
                "blocked_hours": []
            },
            "sunday": {
                "is_available": False,
                "operating_hours": {
                    "start_time": None,
                    "end_time": None
                },
                "blocked_hours": []
            }
        },
        "blocked_dates": []
    }


def get_example_schedule_model():
    return Schedule(
        preffered_timezone="Europe/London",
        daily_schedule=DailySchedule(
            monday=DailyScheduleItem(
                is_available=True,
                operating_hours=TimeSlotModel(
                    start_time=time(10, 0), end_time=time(18, 0)),
                blocked_hours=[TimeSlotModel(
                    start_time=time(14, 0), end_time=time(15, 0))]
            ),
            tuesday=DailyScheduleItem(
                is_available=True,
                operating_hours=TimeSlotModel(
                    start_time=time(10, 0), end_time=time(18, 0)),
                blocked_hours=[TimeSlotModel(
                    start_time=time(14, 0), end_time=time(15, 0))]
            ),
            wednesday=DailyScheduleItem(
                is_available=True,
                operating_hours=TimeSlotModel(
                    start_time=time(10, 0), end_time=time(18, 0)),
                blocked_hours=[]
            ),
            thursday=DailyScheduleItem(
                is_available=True,
                operating_hours=TimeSlotModel(
                    start_time=time(10, 0), end_time=time(18, 0)),
                blocked_hours=[]
            ),
            friday=DailyScheduleItem(
                is_available=True,
                operating_hours=TimeSlotModel(
                    start_time=time(10, 0), end_time=time(18, 0)),
                blocked_hours=[]
            ),
            saturday=DailyScheduleItem(
                is_available=True,
                operating_hours=TimeSlotModel(
                    start_time=time(11, 0), end_time=time(16, 0)),
                blocked_hours=[]
            ),
            sunday=DailyScheduleItem(
                is_available=False,
                operating_hours=TimeSlotModel(start_time=None, end_time=None),
                blocked_hours=[]
            ),
        ),
        blocked_dates=[date(2024, 12, 25), date(2025, 1, 1)]
    )

def get_example_booking():
    return {
        "_id": "64f1a2b9c23eaa0001a55c8b",
        "customer_id": "customer123",
        "merchant_id": "merchant456",
        "service_id": "service789",
        "date_created": "2024-08-28T10:30:00+00:00",
        "booking_status": "CONFIRMED",
        "appointment_date": {
            "start_time": "2024-08-29T15:30:00+00:00",
            "end_time": "2024-08-29T17:00:00+00:00"
        },
        "payment_status": "PAID",
        "location": {
            "coordinates": {
                "latitude": 40.712776,
                "longitude": -74.005974

            },
            "country" : {
                "name": "Canada",
                "code": "CA",
                "currency": {
                    "code": "CAD",
                    "symbol": "CA$",
                    "name": "Canadian Dollar"
                },
            },
            "city":"Cityville",
            "street_address": "123 Main St, Cityville, CV12345",
        },   
    }
