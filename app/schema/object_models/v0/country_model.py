from pydantic import ConfigDict, BaseModel


class Currency(BaseModel):
    code: str
    symbol: str
    name: str
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)


class Country(BaseModel):
    name: str
    code: str
    currency: Currency
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)
