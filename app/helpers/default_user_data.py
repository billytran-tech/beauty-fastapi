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
