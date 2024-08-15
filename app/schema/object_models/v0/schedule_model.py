from datetime import time, date
from pydantic import ConfigDict, BaseModel
from typing import List


class TimeSlotModel(BaseModel):
    start_time: time | None = None
    end_time: time | None = None
    model_config = ConfigDict(populate_by_name=True,
                              arbitrary_types_allowed=True)


class DailyScheduleItem(BaseModel):
    is_available: bool
    operating_hours: TimeSlotModel
    blocked_hours: List[TimeSlotModel]
    model_config = ConfigDict(populate_by_name=True,
                              arbitrary_types_allowed=True)


class DailySchedule(BaseModel):
    monday: DailyScheduleItem
    tuesday: DailyScheduleItem
    wednesday: DailyScheduleItem
    thursday: DailyScheduleItem
    friday: DailyScheduleItem
    saturday: DailyScheduleItem
    sunday: DailyScheduleItem
    model_config = ConfigDict(populate_by_name=True,
                              arbitrary_types_allowed=True)


class Schedule(BaseModel):
    preffered_timezone: str
    daily_schedule: DailySchedule
    blocked_dates: List[date]
    model_config = ConfigDict(populate_by_name=True,
                              arbitrary_types_allowed=True)
