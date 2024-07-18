from datetime import time, date
from pydantic import BaseModel
from typing import List


class TimeSlotModel(BaseModel):
    start_time: time
    end_time: time

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class DailyScheduleItem(BaseModel):
    is_available: bool
    operating_hours: TimeSlotModel
    blocked_hours: List[TimeSlotModel]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class DailySchedule(BaseModel):
    monday: DailyScheduleItem
    tuesday: DailyScheduleItem
    wednesday: DailyScheduleItem
    thursday: DailyScheduleItem
    friday: DailyScheduleItem
    saturday: DailyScheduleItem
    sunday: DailyScheduleItem

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class Schedule(BaseModel):
    preffered_timezone: str
    daily_schedule: DailySchedule
    blocked_dates: List[date]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
