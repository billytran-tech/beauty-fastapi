from pydantic import ConfigDict, BaseModel, Field
from typing import List, Optional
from bson import ObjectId

from app.schema.object_models.v0.id_model import PyObjectId
from app.schema.object_models.v0.location_model import Location
from app.schema.object_models.v0.payment_model import Price


class CreateService(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    service_name: str = Field(...)
    out_call: bool = False
    description: str = Field(...)
    duration_minutes: int = Field(...)
    images: Optional[List[str]] = None
    price: Price = Field(...)
    # TODO[pydantic]: The following keys were removed: `json_encoders`.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    model_config = ConfigDict(
        populate_by_name=True, arbitrary_types_allowed=True, json_encoders={ObjectId: str})


class ProfileServiceResponse(BaseModel):
    id: str = Field(alias="_id")
    service_name: str = Field(...)
    duration_minutes: int = Field(...)
    out_call: bool = False
    description: str = Field(...)
    images: Optional[List[str]] = None
    price: Price = Field(...)
    # TODO[pydantic]: The following keys were removed: `json_encoders`.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    model_config = ConfigDict(
        populate_by_name=True, arbitrary_types_allowed=True, json_encoders={ObjectId: str})


class Service(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    service_name: str = Field(...)
    duration: int = Field(...)
    out_call: bool = Field(...)
    description: str = Field(...)
    images: Optional[List[str]] = None
    price: Price = Field(...)
    owner_id: str = Field(...)
    # TODO[pydantic]: The following keys were removed: `json_encoders`.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    model_config = ConfigDict(
        populate_by_name=True, arbitrary_types_allowed=True, json_encoders={ObjectId: str})


class ServiceOwner(BaseModel):
    username: Optional[str] = None
    name: str
    profile_image_url: Optional[str] = None
    profession: Optional[str] = None
    location: Location
    model_config = ConfigDict(populate_by_name=True,
                              arbitrary_types_allowed=True)


class ServiceSnapshotResponse(BaseModel):
    id: str = Field(alias="_id")
    service_name: str = Field(...)
    duration: int = Field(...)
    out_call: bool = Field(...)
    images: Optional[List[str]] = None
    price: Price = Field(...)
    model_config = ConfigDict(populate_by_name=True,
                              arbitrary_types_allowed=True)


class ServiceSummaryResponse(ServiceSnapshotResponse):
    owner: ServiceOwner
    model_config = ConfigDict(populate_by_name=True,
                              arbitrary_types_allowed=True)


class ServiceResponse(BaseModel):
    id: str = Field(alias="_id")
    service_name: str = Field(...)
    duration_minutes: int = Field(...)
    out_call: bool = Field(...)
    description: str = Field(...)
    owner: ServiceOwner
    images: Optional[List[str]] = None
    price: Price = Field(...)


class UpdateService(BaseModel):
    service_name: str = Field(...)
    duration_minutes: int = Field(...)
    out_call: bool = Field(...)
    description: str = Field(...)
    images: Optional[List[str]] = None
    price: Price = Field(...)
    model_config = ConfigDict(populate_by_name=True,
                              arbitrary_types_allowed=True)
