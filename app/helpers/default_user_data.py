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


# def get_default_location_data():
#     return {
#         "location": {
#             "coordinates": {
#                 "latitude": 0,
#                 "longitude": 0
#             },
#             "country": None,
#             "city": None,
#             "street_address": None,
#         }
#     }
