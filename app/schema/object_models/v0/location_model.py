from pydantic import ConfigDict, BaseModel
from app.schema.object_models.v0.country_model import Country


class Coordinates(BaseModel):
    longitude: float
    latitude: float
    model_config = ConfigDict(populate_by_name=True,
                              arbitrary_types_allowed=True)


class Location(BaseModel):
    country: Country
    city: str
    street_address: str
    coordinates: Coordinates
    model_config = ConfigDict(populate_by_name=True,
                              arbitrary_types_allowed=True)
