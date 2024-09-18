from typing import Optional
from pydantic import ConfigDict, BaseModel


class Currency(BaseModel):
    code: str
    symbol: str
    name: str
    model_config = ConfigDict(populate_by_name=True,
                              arbitrary_types_allowed=True)


class Country(BaseModel):
    name: str
    code: str
    dialing_code: str = None
    currency: Currency
    model_config = ConfigDict(populate_by_name=True,
                              arbitrary_types_allowed=True)


class FullCountryModel(Country):
    dialing_code: str

    model_config = ConfigDict(populate_by_name=True,
                              arbitrary_types_allowed=True)


class CountrySummary(BaseModel):
    value: str
    code: str
    label: str
    model_config = ConfigDict(populate_by_name=True,
                              arbitrary_types_allowed=True)
