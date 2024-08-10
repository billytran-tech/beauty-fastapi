from pydantic import ConfigDict, BaseModel, Field


class NotificationAvenues(BaseModel):
    sms: bool = Field(...)
    email: bool = Field(...)
    whatsapp: bool = Field(...)
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)


class NotificationSettings(BaseModel):
    BookingChanges: NotificationAvenues
    BookingReminders: NotificationAvenues
    SuavUpdates: NotificationAvenues
    SecuritySettings: NotificationAvenues
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)


class ProfileSettings(BaseModel):
    notification_preferences: NotificationSettings
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)
