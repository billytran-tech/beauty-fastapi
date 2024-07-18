from pydantic import BaseModel, Field, AnyHttpUrl
from typing import Optional, List
from bson import ObjectId
from app.schema.object_models.v0.payment_model import Price
from app.schema.object_models.v0.id_model import PyObjectId


class ServiceAddOn(BaseModel):
    name: str
    description: str
    price: Price

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class OutCallParameter(BaseModel):
    out_call: bool
    radius: int

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class Service(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(...)
    description: str = Field(...)
    duration_minutes: int = Field(...)
    base_price: Price
    custom_options: List[ServiceAddOn] = Field(...)
    images: Optional[AnyHttpUrl] = Field(...)
    out_call: OutCallParameter
    owner_id: str = Field(...)
    price: Price = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
