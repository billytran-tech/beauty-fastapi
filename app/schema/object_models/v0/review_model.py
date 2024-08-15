from pydantic import ConfigDict, BaseModel, Field, AnyHttpUrl
from typing import List
from app.schema.object_models.v0.id_model import PyObjectId


class Review(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    booking_id: str
    customer_id: str
    merchant_id: str
    cleanliness_rating: int
    service_rating: int
    comments: str
    review_images: List[AnyHttpUrl]
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)
