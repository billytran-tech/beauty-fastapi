from datetime import datetime
from bson import ObjectId
from pydantic import ConfigDict, BaseModel, Field
from typing import List
from app.schema.enums import BookingStatusEnum, PaymentStatusEnum
from app.schema.object_models.v0.location_model import Location
from app.schema.object_models.v0.id_model import PyObjectId
from app.schema.object_models.v0.payment_model import Transaction


# class AppointmentDate(BaseModel):

class Booking(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    customer_id: str
    merchant_id: str
    service_id: str
    date_created: datetime
    booking_status: BookingStatusEnum
    appointment_date: datetime
    payment_status: PaymentStatusEnum
    location: Location
    payment_details: List[Transaction]
    # TODO[pydantic]: The following keys were removed: `json_encoders`.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True, json_encoders={ObjectId: str})
