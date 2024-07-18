from pydantic import BaseModel, Field


class NotificationAvenues(BaseModel):
    sms: bool = Field(...)
    email: bool = Field(...)
    whatsapp: bool = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class NotificationSettings(BaseModel):
    BookingChanges: NotificationAvenues
    BookingReminders: NotificationAvenues
    SuavUpdates: NotificationAvenues
    SecuritySettings: NotificationAvenues

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class Settings(BaseModel):
    notification_preferences: NotificationSettings

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
