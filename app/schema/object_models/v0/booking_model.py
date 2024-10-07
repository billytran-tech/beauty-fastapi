import datetime
from bson import ObjectId
from pydantic import AnyHttpUrl, ConfigDict, BaseModel, Field
from typing import List, Optional
from app.schema.enums.enums import BookingStatusEnum, PaymentStatusEnum
from app.schema.object_models.v0.location_model import Location
from app.schema.object_models.v0.id_model import PyObjectId
from app.schema.object_models.v0.payment_model import Price, Transaction


class AppointmentDate(BaseModel):
    start_time: datetime.datetime
    end_time: datetime.datetime

    model_config = ConfigDict(populate_by_name=True,
                              arbitrary_types_allowed=True)


class AppointmentStartDate(BaseModel):
    date: datetime.datetime

    model_config = ConfigDict(populate_by_name=True,
                              arbitrary_types_allowed=True)


class CreateBooking(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    service_id: str
    appointment_date: AppointmentStartDate
    model_config = ConfigDict(
        populate_by_name=True, arbitrary_types_allowed=True, json_encoders={ObjectId: str})


class ClientObject(BaseModel):
    id: str = Field(alias='user_id')
    name: str
    profile_image_url: Optional[str] = None
    # contact_info: Contact

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class MerchantObject(BaseModel):
    id: str = Field(alias='_id')
    profile_image_url: AnyHttpUrl | None
    name: str

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class ServiceObject(BaseModel):
    id: str = Field(alias="_id")
    service_name: str = Field(...)
    duration_minutes: int = Field(...)
    out_call: bool = Field(...)
    description: str = Field(...)
    images: Optional[List[str]] = None
    price: Price = Field(...)
    model_config = ConfigDict(
        populate_by_name=True, arbitrary_types_allowed=True, json_encoders={ObjectId: str})


class MerchantBookingField(MerchantObject):
    id: str
    model_config = ConfigDict(populate_by_name=True,
                              arbitrary_types_allowed=True)


class ClientBookingField(MerchantObject):
    id: str
    model_config = ConfigDict(populate_by_name=True,
                              arbitrary_types_allowed=True)


class BookingFullModel(BaseModel):
    id: str = Field(alias="_id")
    customer: ClientBookingField
    merchant: MerchantBookingField
    service: ServiceObject
    date_created: datetime.datetime = datetime.datetime.now(datetime.UTC)
    appointment_date: AppointmentDate
    booking_status: BookingStatusEnum
    payment_status: PaymentStatusEnum
    appointment_location: Location
    # comments: Optional[str]
    model_config = ConfigDict(
        populate_by_name=True, arbitrary_types_allowed=True)


class Booking(BaseModel):
    # id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    customer_id: str
    merchant_id: str
    service_id: str
    date_created: datetime.datetime
    booking_status: BookingStatusEnum
    appointment_date: AppointmentDate
    payment_status: PaymentStatusEnum
    location: Location
    # payment_details: List[Transaction]
    # TODO[pydantic]: The following keys were removed: `json_encoders`.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    model_config = ConfigDict(
        populate_by_name=True, arbitrary_types_allowed=True, json_encoders={ObjectId: str})
