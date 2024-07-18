from bson import ObjectId
from pydantic import BaseModel, Field, AnyHttpUrl
from typing import List
from app.schema.object_models.v0.id_model import PyObjectId
from app.schema.object_models.v0.location_model import Location
from app.schema.object_models.v0.settings_model import Settings
from app.schema.object_models.v0.schedule_model import Schedule


class WishList(BaseModel):
    name: str
    stylists: List[str]
    services: List[str]


class User(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    auth0id: str
    name: str
    profile_image: AnyHttpUrl

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class Customer(User):
    location: Location
    wish_list: List[WishList]
    settings: Settings

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class Merchant(User):
    profile_public: bool
    username: str
    profession: str
    location: Location
    bio: str
    settings: Settings
    schedule: Schedule
