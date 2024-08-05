from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel, Field
from typing import Optional
from app.schema.object_models.v0.id_model import PyObjectId
from app.schema.enums import NotificationType

class Notification(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    booking_id: str
    customer_id: str
    notification_type: NotificationType
    status: str
    message: str
    date_created: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
