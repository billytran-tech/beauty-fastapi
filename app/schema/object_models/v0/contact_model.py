from typing import Optional
from pydantic import ConfigDict, BaseModel


class Email(BaseModel):
    email: str
    is_verified: bool = False
    model_config = ConfigDict(populate_by_name=True,
                              arbitrary_types_allowed=True)


class UpdatePhoneNumber(BaseModel):
    phone_number: str
    model_config = ConfigDict(populate_by_name=True,
                              arbitrary_types_allowed=True)


class PhoneNumber(BaseModel):
    dialing_code: str
    phone_number: int
    is_verified: bool = False
    model_config = ConfigDict(populate_by_name=True,
                              arbitrary_types_allowed=True)


class ContactInfo(BaseModel):
    email: Optional[Email] = None
    phone_number: PhoneNumber

    model_config = ConfigDict(populate_by_name=True,
                              arbitrary_types_allowed=True)
