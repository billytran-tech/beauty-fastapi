from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List
from bson import ObjectId
from app.schema.object_models.v0.country_model import Currency
from app.schema.object_models.v0.id_model import PyObjectId
from app.schema.enums import PaymentGatewayEnum, TransactionTypeEnum, TransactionStatusEnum


class Price(BaseModel):
    amount: Decimal  # The monetary amount, represented with high precision using Decimal
    currency: Currency

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class Transaction(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    payment_gateway: PaymentGatewayEnum
    transaction_type: TransactionTypeEnum
    amount: Decimal
    currency: Currency
    transaction_date: datetime
    status: TransactionStatusEnum
    payment_method: str
    description: str
    # gateway_response: GatewayResponse

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
