from pydantic import BaseModel
from app.schema.object_models.v0.country_model import Country


class Location(BaseModel):
    country: Country
    city: str
    street_address: str
    longitude: float
    latitude: float

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
