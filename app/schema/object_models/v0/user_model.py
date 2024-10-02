from bson import ObjectId
from datetime import time
from pydantic import ConfigDict, BaseModel, Field, AnyHttpUrl
from typing import List, Optional
from app.schema.object_models.v0.id_model import PyObjectId
from app.schema.object_models.v0.location_model import Coordinates, Location
from app.schema.object_models.v0.service_model import ServiceSnapshotResponse
from app.schema.object_models.v0.settings_model import ProfileSettings
from app.schema.object_models.v0.schedule_model import Schedule
from app.schema.object_models.v0.contact_model import ContactInfo
from app.schema.object_models.v0.country_model import FullCountryModel


class WishList(BaseModel):
    name: str
    stylists: List[str]
    services: List[str]


class RegisterUser(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    first_name: str
    last_name: str
    country_code: str
    phone_number: int
    model_config = ConfigDict(populate_by_name=True,
                              arbitrary_types_allowed=True, json_encoders={ObjectId: str})


class UserProfile(BaseModel):
    id: str = Field(alias='_id')
    user_id: str
    first_name: str
    last_name: str
    country_code: str
    contact_info: ContactInfo
    model_config = ConfigDict(populate_by_name=True,
                              arbitrary_types_allowed=True)


class UserProfileResponse(BaseModel):
    first_name: str
    last_name: str
    country: FullCountryModel
    # contact_info: ContactInfo

    model_config = ConfigDict(populate_by_name=True,
                              arbitrary_types_allowed=True)


class User(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    name: str
    profile_image: AnyHttpUrl
    # TODO[pydantic]: The following keys were removed: `json_encoders`.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    model_config = ConfigDict(
        populate_by_name=True, arbitrary_types_allowed=True, json_encoders={ObjectId: str})


class Customer(User):
    location: Location
    wish_list: List[WishList]
    settings: ProfileSettings
    model_config = ConfigDict(populate_by_name=True,
                              arbitrary_types_allowed=True)


class Merchant(User):
    profile_public: bool
    username: str
    profession: str
    location: Location
    bio: str
    settings: ProfileSettings
    schedule: Schedule


class MerchantModelForComparison(BaseModel):
    id: str = Field(alias='_id')
    user_id: str
    model_config = ConfigDict(populate_by_name=True,
                              arbitrary_types_allowed=True)


class CreateCustomer(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    name: str
    country: str
    profile_picture_url: Optional[AnyHttpUrl] = None
    wishlists: Optional[List[WishList]] = None
    # TODO[pydantic]: The following keys were removed: `json_encoders`.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    model_config = ConfigDict(
        populate_by_name=True, arbitrary_types_allowed=True, json_encoders={ObjectId: str})


class InsertDBCustomer(BaseModel):
    id: str = Field(alias='_id')
    user_id: str
    name: str
    country: str
    profile_picture_url: Optional[AnyHttpUrl] = None
    wishlists: Optional[List[WishList]] = None
    settings: ProfileSettings
    model_config = ConfigDict(populate_by_name=True,
                              arbitrary_types_allowed=True)


class UpdateCustomerData(BaseModel):
    name: str
    country: str
    wishlists: Optional[List[WishList]] = None
    model_config = ConfigDict(populate_by_name=True,
                              arbitrary_types_allowed=True)


class CustomerDataResponse(BaseModel):
    name: str
    country: str
    profile_picture_url: Optional[AnyHttpUrl] = None
    wishlists: Optional[List[WishList]] = None
    settings: ProfileSettings
    model_config = ConfigDict(populate_by_name=True,
                              arbitrary_types_allowed=True)


# class TimeSlotModel(BaseModel):
#     # constr(regex=r'^([0-1][0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])$')
#     start_time: time
#     # constr(regex=r'^([0-1][0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])$')
#     end_time: time
#     model_config = ConfigDict(populate_by_name=True,
#                               arbitrary_types_allowed=True)


# class OperatingHours(BaseModel):
#     opening_time: time
#     closing_time: time
#     model_config = ConfigDict(populate_by_name=True,
#                               arbitrary_types_allowed=True)


# class DailyScheduleItem(BaseModel):
#     isActive: bool = False
#     operating_hours: Optional[OperatingHours] = None
#     blocked_out_time: Optional[TimeSlotModel] = None
#     model_config = ConfigDict(populate_by_name=True,
#                               arbitrary_types_allowed=True)


# class DailySchedule(BaseModel):
#     monday: DailyScheduleItem
#     tuesday: DailyScheduleItem
#     wednesday: DailyScheduleItem
#     thursday: DailyScheduleItem
#     friday: DailyScheduleItem
#     saturday: DailyScheduleItem
#     sunday: DailyScheduleItem


# class Schedule(BaseModel):
#     preffered_timezone: str
#     daily_schedule: DailySchedule
#     blocked_dates: List[str] = []


# class Coordinates(BaseModel):
#     longitude: float
#     latitude: float
#     model_config = ConfigDict(populate_by_name=True,
#                               arbitrary_types_allowed=True)


# class Location(BaseModel):
#     coordinates: Optional[Coordinates] = None
#     country: str
#     city: str
#     street_address: Optional[str] = None
#     model_config = ConfigDict(populate_by_name=True,
#                               arbitrary_types_allowed=True)


class MerchantProfileData(BaseModel):
    name: str | None = None
    username: str
    profession: Optional[str] = None
    location: Location = None
    profile_picture_url: Optional[AnyHttpUrl] = None
    intro_video_url: Optional[AnyHttpUrl] = None
    schedule: Schedule
    bio: Optional[str] = None
    settings: ProfileSettings
    model_config = ConfigDict(populate_by_name=True,
                              arbitrary_types_allowed=True)


class CreateMerchantData(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    username: str
    name: str
    profession: str
    profile_image_url: Optional[str] = None
    # schedule: Schedule
    location: Location
    bio: str
    model_config = ConfigDict(populate_by_name=True,
                              arbitrary_types_allowed=True, json_encoders={ObjectId: str})


class MerchantDBStructure(BaseModel):
    username_id: str
    public: bool = False
    user_id: str
    name: str
    profession: str
    profile_picture_url: Optional[str] = None
    intro_video_url: Optional[str] = None
    schedule: Schedule
    location: Location
    bio: Optional[str] = None
    settings: ProfileSettings
    model_config = ConfigDict(populate_by_name=True,
                              arbitrary_types_allowed=True)


class MerchantDBInsert(MerchantDBStructure):
    id: str = Field(alias='_id')
    model_config = ConfigDict(populate_by_name=True,
                              arbitrary_types_allowed=True)


class UpdateMerchantData(BaseModel):
    name: str
    username: str
    profession: str
    # schedule: Schedule
    location: Location
    bio: Optional[str] = None
    model_config = ConfigDict(populate_by_name=True,
                              arbitrary_types_allowed=True)


class MerchantCardResponse(BaseModel):
    username: str
    image_url: Optional[AnyHttpUrl] = None
    header_name: str
    location: Location
    profession: Optional[str] = None
    model_config = ConfigDict(populate_by_name=True,
                              arbitrary_types_allowed=True)


class MerchantDataWithoutSchedule(BaseModel):
    name: str
    profession: Optional[str] = None
    location: Location
    profile_picture_url: Optional[AnyHttpUrl] = None
    intro_video_url: Optional[AnyHttpUrl] = None
    bio: Optional[str] = None
    model_config = ConfigDict(populate_by_name=True,
                              arbitrary_types_allowed=True)


class MerchantQueryResponseData(BaseModel):
    username: str
    name: str
    # contact_info: Contact
    profile: MerchantDataWithoutSchedule
    services: List[ServiceSnapshotResponse]
    model_config = ConfigDict(populate_by_name=True,
                              arbitrary_types_allowed=True)


class MerchantBasicInfo(BaseModel):
    name: str
    username: str
    profession: str
    bio: Optional[str] = None
    model_config = ConfigDict(populate_by_name=True,
                              arbitrary_types_allowed=True)


class UpdateIntroVideoURL(BaseModel):
    intro_video_url: str
    model_config = ConfigDict(populate_by_name=True,
                              arbitrary_types_allowed=True)


class UpdateProfilePictureURL(BaseModel):
    profile_picture_url: str
    model_config = ConfigDict(populate_by_name=True,
                              arbitrary_types_allowed=True)
